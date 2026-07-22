from datetime import timedelta

from celery import Celery

from . import config


app = Celery("tasks", broker=config.BROKER, backend=config.RESULT_BACKEND)

beat_schedule = {
    "scanned.clean-documents": {
        "task": "scanned.clean_documents",
        "schedule": timedelta(hours=12),
    },
    "scanned.notify-new-documents": {
        "task": "scanned.notify_new_documents",
        "schedule": timedelta(hours=24),
    },
    "validate.clean_emails": {
        "task": "validate.clean_emails",
        "schedule": timedelta(seconds=config.CLEAN_EMAILS_TIMEOUT),
    },
    "validate.clean_alerts_with_past_dates": {
        "task": "validate.clean_alerts_with_past_dates",
        "schedule": timedelta(seconds=config.CLEAN_EMAILS_TIMEOUT),
    },
}

app.conf.beat_schedule = beat_schedule
# La codificación NormTrace va a su propia cola para no bloquear el tagger.
_TASK_ROUTES = {"normtrace.analyze_units": {"queue": "normtrace"}}
app.conf.task_routes = _TASK_ROUTES

# Resiliencia de arranque: en un PaaS el broker puede no estar listo cuando el
# worker inicia (o su URL aún no está wireada). Reintentar en vez de salir con
# error evita que el deploy se marque "failed" en bucle; en cuanto el broker
# responde, el worker se conecta solo.
_BROKER_RESILIENCE = {
    "broker_connection_retry_on_startup": True,
    "broker_connection_max_retries": None,  # reintenta indefinidamente
}
app.conf.update(_BROKER_RESILIENCE)


def init():
    global app
    app = Celery("tasks", broker=config.BROKER, backend=config.RESULT_BACKEND)
    app.conf.beat_schedule = beat_schedule
    app.conf.task_routes = _TASK_ROUTES
    app.conf.update(_BROKER_RESILIENCE)


from .alerts import *
from .tagger import *
from .validate import *
from .scanned import *
from . import normtrace
