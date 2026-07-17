import codecs
import logging
import pickle
import subprocess
import tempfile
from os.path import splitext
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
from pptx import Presentation

from legal_segmenter import segment as segment_legal

import tipi_tasks
from tipi_backend.api import cache
from tipi_backend.api.business import get_tags, get_kbs
from tipi_backend.api.request_models import KbQuery
from tipi_backend.settings import Config


log = logging.getLogger(__name__)

router = APIRouter(prefix="/tagger", tags=["tagger"])


def filter_tags(result, kb):
    tags = result["result"]["tags"]
    new_topics = []
    new_tags = []
    for tag in tags:
        if tag["knowledgebase"] in kb:
            new_tags.append(tag)
            new_topics.append(tag["topic"])
    new_topics = list(set(new_topics))
    result["result"]["topics"] = new_topics
    result["result"]["tags"] = new_tags
    return result


def remove_fields(result):
    tags = result["result"]["tags"]
    for tag in tags:
        del tag["public"]


def units_with_tags(content, tags, kb):
    """Segmenta el texto (etapa 2) y devuelve `(total_unidades, unidades_con_tags)`.

    Cada unidad con tags incluye su `text` (necesario para la codificación
    NormTrace de la etapa 3). Las unidades sin coincidencias se descartan.
    """
    units = segment_legal(content)
    hit = []
    for unit in units:
        unit_result = tipi_tasks.tagger.extract_tags_from_text(unit.text, tags)
        unit_result = filter_tags(unit_result, kb)
        remove_fields(unit_result)
        unit_tags = unit_result["result"]["tags"]
        if not unit_tags:
            continue
        hit.append(
            {
                "unit_id": unit.unit_id,
                "unit_type": unit.unit_type,
                "number": unit.number,
                "heading": (unit.heading or "")[:200],
                "text": unit.text,
                "parent_id": unit.parent_id,
                "topics": unit_result["result"]["topics"],
                "tags": unit_tags,
            }
        )
    return len(units), hit


def segment_and_tag(content, tags, kb):
    """Bloque `segmentation` (etapa 2) para la respuesta: conteos por unidad, sin
    incluir el texto completo de cada unidad (para no inflar la respuesta)."""
    total, hit = units_with_tags(content, tags, kb)
    units_out = [{k: v for k, v in u.items() if k != "text"} for u in hit]
    return {
        "mode": "legal",
        "units_total": total,
        "units_with_tags": len(units_out),
        "units": units_out,
    }


def _extract_text_from_file(file: UploadFile) -> str:
    with tempfile.NamedTemporaryFile(
        prefix="tipiscanner_", suffix=splitext(file.filename)[1]
    ) as f:
        f.write(file.file.read())
        f.seek(0)
        mimetype = file.content_type
        if mimetype == "text/plain":
            text = f.read().decode("utf-8").strip()
        elif mimetype == "application/pdf":
            text = extract_pdf_text(f.name).strip()
        elif mimetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(f)
            text = "\n".join([para.text for para in doc.paragraphs]).strip()
        elif mimetype == "application/msword":
            result = subprocess.run(
                ["antiword", f.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if result.returncode != 0:
                raise Exception(
                    f"Error al leer el archivo .doc: {result.stderr.decode('utf-8')}"
                )
            text = result.stdout.decode("utf-8").strip()
        elif mimetype == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            ppt = Presentation(f)
            text = "\n".join(
                [
                    shape.text
                    for slide in ppt.slides
                    for shape in slide.shapes
                    if hasattr(shape, "text")
                ]
            ).strip()
        else:
            raise HTTPException(
                status_code=400,
                detail="Formato no soportado. Por favor, utilice un archivo .txt, .pdf, .docx, .doc o .pptx.",
            )
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Error al obtener el texto del fichero proporcionado. Pruebe con otro fichero.",
        )
    return text


@router.post("/")
def extract(
    text: Annotated[str, Form()] = "",
    file: Annotated[UploadFile | str | None, File()] = None,
    knowledgebase: Annotated[str, Form()] = "",
    segment: Annotated[str, Form()] = "",
    deep: Annotated[bool, Form()] = False,
):
    """Etiqueta el texto y devuelve los temas (ODS) y etiquetas que coinciden.

    Con `segment=legal` añade un bloque `segmentation` con los conteos por unidad
    jurídica (artículo, fracción, inciso, transitorio) del texto.

    Con `deep=true` encola además la codificación estructural NormTrace (etapa 3,
    asíncrona) de las unidades con tags y devuelve `normtrace_task_id`; el bloque
    `structural` se recupera en `GET /tagger/deep/{id}` cuando termina.
    """
    try:
        # Blank knowledgebase = no filter (all public KBs), matching Flask's default.
        # The empty default also stops Swagger "Try it out" from sending `"string"`.
        kb = get_kbs({"knowledgebase": knowledgebase or None})

        cache_key = Config.CACHE_TAGS
        tags = cache.get(cache_key)
        if tags is None:
            tags = get_tags()
            cache.set(cache_key, tags, timeout=5 * 60)
        tags = codecs.encode(pickle.dumps(tags), "base64").decode()
        tipi_tasks.init()

        content = ""
        if text:
            content = text
        elif isinstance(file, UploadFile):
            content = _extract_text_from_file(file)

        text_length = len(content.split())

        if text_length >= Config.TAGGER_MAX_WORDS:
            task = tipi_tasks.tagger.extract_tags_from_text.apply_async((content, tags))
            eta_time = int((text_length / 1000) * 4)
            return {
                "status": "PROCESSING",
                "task_id": task.id,
                "estimated_time": eta_time,
            }

        result = tipi_tasks.tagger.extract_tags_from_text(content, tags)
        result = filter_tags(result, kb)
        remove_fields(result)

        # Etapa 2/3 opcionales: segmentación jurídica y codificación NormTrace.
        if (segment == "legal" or deep) and content:
            total, hit = units_with_tags(content, tags, kb)
            result["segmentation"] = {
                "mode": "legal",
                "units_total": total,
                "units_with_tags": len(hit),
                "units": [{k: v for k, v in u.items() if k != "text"} for u in hit],
            }
            # Etapa 3: encola la codificación estructural (cola normtrace).
            if deep and hit:
                task = tipi_tasks.normtrace.analyze_units.apply_async((hit,))
                result["normtrace_task_id"] = task.id

        return result
    except HTTPException:
        raise
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/deep/{id}")
def normtrace_result(id: str):
    """Devuelve el bloque `structural` (codificación NormTrace) de la tarea deep.

    Mientras la tarea no termina responde `{status: PENDING|STARTED}`; al terminar,
    `{status: SUCCESS, structural: {...}}` con las unidades codificadas (cada una
    con `confidence_level` y `review_status`).
    """
    try:
        tipi_tasks.init()
        return tipi_tasks.normtrace.check_status_task(id)
    except Exception as e:
        log.error(e)
        return JSONResponse(status_code=404, content={"Error": "No task found"})


@router.get("/result/{id}")
def tagger_result(id: str, query: Annotated[KbQuery, Query()]):
    """Devuelve el resultado de la tarea de etiquetado asíncrona."""
    try:
        tipi_tasks.init()
        result = tipi_tasks.tagger.check_status_task(id)

        kb = get_kbs(query.model_dump())
        if result["status"] == "SUCCESS":
            result = filter_tags(result, kb)
            remove_fields(result)
        return result
    except Exception as e:
        log.error(e)
        return JSONResponse(status_code=404, content={"Error": "No task found"})
