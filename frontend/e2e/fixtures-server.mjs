// Servidor de fixtures para los tests e2e de invariantes (adenda v6.2 §3/§4).
// Sirve el dist compilado con fallback SPA y responde el API de Huella/Minutas
// con datos representativos y estables (sin depender de un backend real).
// Uso: import { startServer } from './fixtures-server.mjs'
import http from 'node:http';
import { readFileSync, existsSync, statSync } from 'node:fs';
import { extname, join, normalize, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const DEFAULT_DIST = join(HERE, '..', 'dist');

const ODS = {
  1:['#e5243b','Fin de la pobreza'],2:['#dda63a','Hambre cero'],3:['#4c9f38','Salud y bienestar'],
  4:['#c5192d','Educación de calidad'],5:['#ff3a21','Igualdad de género'],6:['#26bde2','Agua limpia y saneamiento'],
  7:['#fcc30b','Energía asequible y no contaminante'],8:['#a21942','Trabajo decente y crecimiento económico'],
  9:['#fd6925','Industria, innovación e infraestructura'],10:['#dd1367','Reducción de las desigualdades'],
  11:['#fd9d24','Ciudades y comunidades sostenibles'],12:['#bf8b2e','Producción y consumo responsables'],
  13:['#3f7e44','Acción por el clima'],14:['#0a97d9','Vida submarina'],15:['#56c02b','Vida de ecosistemas terrestres'],
  16:['#00689d','Paz, justicia e instituciones sólidas'],17:['#19486a','Alianzas para lograr los objetivos'],
};
const catalogos = { ods: Object.fromEntries(Object.entries(ODS).map(([k,v])=>[k,{color:v[0],nombre_es:v[1]}])), metas: [] };
const pesos = {16:22,3:16,5:14,6:12,8:9,10:8,4:7,11:6,1:6,7:4,13:4,9:3,12:3,2:3,17:2,15:2,14:1};
const bolsa=[]; for(const [k,w] of Object.entries(pesos)) for(let i=0;i<w;i++) bolsa.push(k);
const pick=(seed)=>bolsa[seed % bolsa.length];
const temas=['salario mínimo','vivienda adecuada','derecho al agua','igualdad sustantiva','acceso a la salud','educación inicial','trabajo digno','justicia cotidiana','pueblos indígenas','medio ambiente sano','movilidad urbana','protección de datos','cambio climático','pesca responsable','energía limpia'];
const grupos=['Morena','PAN','PRI','MC','PT','PVEM','PRD'];
const estatusList=[['publicada_dof','Publicada en el DOF'],['en_revisora','En cámara revisora'],['devuelta','Devuelta a origen']];
const minutas=[];
for(let i=0;i<139;i++){
  const st=estatusList[i%3]; const ods=(i%5===0)?null:pick(i*7+3); const sec=(i%4!==0);
  minutas.push({ id:'min'+i, clave:`M-${65+(i%3)}-${100+i}`, denominacion:`Minuta con proyecto de decreto sobre ${temas[i%temas.length]}`,
    tema:temas[(i+3)%temas.length], estatus:st[0], estatus_label:st[1],
    grupos_parlamentarios: sec?[grupos[i%grupos.length]]:[], origen: sec?null:(i%7===0?null:'Senado'),
    ods_principal:ods, ods_secundarios: ods?[pick(i*3+1)]:[], metas: ods?[`${ods}.${1+(i%3)}`]:[],
    confianza:(i%6===0)?'alta':(i%6===1?'pendiente':null) });
}
const iniciativas=[];
for(let i=0;i<200;i++){
  const ods=(i%6===0)?null:pick(i*11+5); const aprob=(i%9===0);
  iniciativas.push({ id:'ini'+i, num:i+1, denominacion:`Iniciativa que reforma la ley en materia de ${temas[i%temas.length]}`,
    tema:temas[(i+1)%temas.length], ods_principal:ods, ods_secundarios: ods?[pick(i*5+2)]:[],
    metas: ods?[`${ods}.${1+(i%4)}`]:[], estatus: aprob?'Aprobada':'En proceso',
    seccion: aprob?'Aprobadas en el periodo':'En comisiones', confianza:(i%5===0)?'alta':null });
}
const agrupa=(list,key)=>{const m={};list.forEach(x=>{const k=x[key]||'sin';m[k]=(m[k]||0)+1;});return m;};
const porOdsMin = Object.entries(agrupa(minutas.filter(m=>m.ods_principal),'ods_principal'))
  .map(([ods,principal])=>({ods:+ods,principal,secundario:Math.round(principal*0.4)}))
  .sort((a,b)=>(b.principal+b.secundario)-(a.principal+a.secundario));
const minResumen={ corte:'30 jun 2026', kpis:{ minutas_totales:minutas.length,
  con_correspondencia_ods:minutas.filter(m=>m.ods_principal).length,
  pct_con_correspondencia_ods: Math.round(minutas.filter(m=>m.ods_principal).length/minutas.length*1000)/10,
  atribucion_documentada:minutas.filter(m=>m.grupos_parlamentarios.length||m.origen).length,
  sin_origen_documentado:minutas.filter(m=>!m.grupos_parlamentarios.length&&!m.origen).length },
  por_estatus: estatusList.map(([e,l])=>({estatus:e,etiqueta:l,n:minutas.filter(m=>m.estatus===e).length})),
  por_anio:[{anio:2024,n:44},{anio:2025,n:61},{anio:2026,n:34}],
  por_origen:[{origen:'Cámara de Diputados',n:78},{origen:'Senado',n:41},{origen:'Congresos estatales',n:12},{origen:'Sin documentar',n:8,por_documentar:true}],
  por_ods: porOdsMin };
const porOdsIni = Object.entries(agrupa(iniciativas.filter(i=>i.ods_principal),'ods_principal')).map(([ods,n])=>({ods:+ods,n}));
const huellaEjec={ corte:'30 jun 2026', normtrace_vitrina:'ini5',
  kpis:{ iniciativas_presentadas:iniciativas.length, aprobadas:iniciativas.filter(i=>i.seccion.startsWith('Aprobadas')).length, ods_dominante:'16' },
  por_ods: porOdsIni.sort((a,b)=>b.n-a.n) };
// Snapshot de solo lectura generado de
// normtrace/03_tables/legislative_mapping/gold/lga_ods6_mapeo_normtrace.csv
// (34 registros, dato de investigación; no se muta). Patch v8 §B: alimenta la
// matriz NormTrace (ficha del expediente + vista previa de la escena del agua).
const normtraceLga34 = [
  {estandar:"ODS 6.1 Acceso universal agua potable asequible",disposicion:"Art. 1",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"fuerte",federalismo_fit:"fuerte",tipo_brecha:"",nota:"Objeto: reglamenta el DH al agua del art. 4o CPEUM; distribuye competencias"},
  {estandar:"ODS 6.1 Acceso universal agua potable asequible",disposicion:"Art. 7 fracc. I-VI",rol_correspondencia:"sustantivo",cobertura:"completa",actor_fit:"medio",procedimiento_fit:"debil",coordinacion_fit:"no_aplica",enforcement_fit:"debil",salvaguarda_derechos_fit:"fuerte",federalismo_fit:"no_aplica",tipo_brecha:"",nota:"Reproduce casi literalmente los elementos de la OG 15: accesibilidad, informacion, aceptabilidad, asequibilidad, calidad, disponibilidad"},
  {estandar:"ODS 6.1 Acceso universal agua potable asequible",disposicion:"Art. 9 parr. 1",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"fuerte",enforcement_fit:"debil",salvaguarda_derechos_fit:"fuerte",federalismo_fit:"fuerte",tipo_brecha:"brecha_procedimental",nota:"Progresividad y 'cantidad minima establecida en los estandares internacionales': sin numeral ni remision a NOM"},
  {estandar:"ODS 6.1 Acceso universal agua potable asequible",disposicion:"Art. 9 parr. 2",rol_correspondencia:"sustantivo",cobertura:"completa",actor_fit:"fuerte",procedimiento_fit:"medio",coordinacion_fit:"no_aplica",enforcement_fit:"medio",salvaguarda_derechos_fit:"fuerte",federalismo_fit:"no_aplica",tipo_brecha:"",nota:"Prohibicion de corte total por falta de pago + minimo vital: la obligacion mas operativa y justiciable de la ley"},
  {estandar:"ODS 6.1 Acceso universal agua potable asequible",disposicion:"Art. 25 fracc. I y IV",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"fuerte",tipo_brecha:"",nota:"Federacion: politica nacional con el agua como derecho prioritario; privilegiar DH agua en administracion de aguas nacionales"},
  {estandar:"ODS 6.1 Acceso universal agua potable asequible",disposicion:"Art. 28 fracc. I-II",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"fuerte",tipo_brecha:"",nota:"Municipios: garantizar servicios y priorizarlos en programacion y presupuestacion"},
  {estandar:"ODS 6.2 Saneamiento e higiene, atencion a mujeres y ninas",disposicion:"Art. 8 parr. 2",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"debil",procedimiento_fit:"debil",coordinacion_fit:"no_aplica",enforcement_fit:"debil",salvaguarda_derechos_fit:"fuerte",federalismo_fit:"no_aplica",tipo_brecha:"",nota:"Define saneamiento como acceso a instalaciones seguras, dignas, asequibles y culturalmente aceptables"},
  {estandar:"ODS 6.2 Saneamiento e higiene, atencion a mujeres y ninas",disposicion:"Art. 15 fracc. IV y VI",rol_correspondencia:"sustantivo",cobertura:"completa",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"fuerte",federalismo_fit:"medio",tipo_brecha:"",nota:"Integridad de mujeres y ninas en servicios; menstruacion digna con acceso prioritario: correspondencia directa con el enfasis de genero de la meta 6.2"},
  {estandar:"ODS 6.2 Saneamiento e higiene, atencion a mujeres y ninas",disposicion:"Art. 16",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"medio",procedimiento_fit:"debil",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"medio",tipo_brecha:"brecha_procedimental",nota:"NOMs y disposiciones tecnicas locales conforme a estandares internacionales; sin plazo de emision"},
  {estandar:"ODS 6.2 Saneamiento e higiene, atencion a mujeres y ninas",disposicion:"Art. 17",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"fuerte",tipo_brecha:"",nota:"Municipios y comunidades deberan contar con sistemas de saneamiento adecuados; sin plazo ni meta de cobertura"},
  {estandar:"ODS 6.3 Calidad, aguas residuales, reuso",disposicion:"Art. 4 fracc. X",rol_correspondencia:"contextual_habilitante",cobertura:"contextual",actor_fit:"no_aplica",procedimiento_fit:"no_aplica",coordinacion_fit:"no_aplica",enforcement_fit:"no_aplica",salvaguarda_derechos_fit:"medio",federalismo_fit:"no_aplica",tipo_brecha:"",nota:"Definicion de saneamiento alineada a estandares internacionales"},
  {estandar:"ODS 6.3 Calidad, aguas residuales, reuso",disposicion:"Art. 18",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"fuerte",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"fuerte",tipo_brecha:"brecha_procedimental",nota:"Incremento progresivo de cobertura de saneamiento y tratamiento; sin indicadores ni denominadores propios"},
  {estandar:"ODS 6.3 Calidad, aguas residuales, reuso",disposicion:"Art. 19",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"fuerte",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"medio",tipo_brecha:"",nota:"Incentivos para saneamiento, tratamiento y reutilizacion (reuso = componente explicito de la meta 6.3)"},
  {estandar:"ODS 6.3 Calidad, aguas residuales, reuso",disposicion:"Art. 27 fracc. II-III",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"fuerte",tipo_brecha:"",nota:"Entidades: prevencion y control de contaminacion; regulacion de tratamiento y reuso en su jurisdiccion"},
  {estandar:"ODS 6.4 Uso eficiente y extraccion sostenible",disposicion:"Art. 6 fracc. VIII",rol_correspondencia:"contextual_habilitante",cobertura:"contextual",actor_fit:"no_aplica",procedimiento_fit:"no_aplica",coordinacion_fit:"no_aplica",enforcement_fit:"no_aplica",salvaguarda_derechos_fit:"medio",federalismo_fit:"no_aplica",tipo_brecha:"",nota:"Principio de sustentabilidad"},
  {estandar:"ODS 6.4 Uso eficiente y extraccion sostenible",disposicion:"Art. 31 fracc. XII-XIII",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"medio",procedimiento_fit:"medio",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"medio",tipo_brecha:"brecha_administrativa",nota:"Estrategia Nacional debe incluir erradicacion de sobreexplotacion y de distribucion inequitativa; operacion queda en LAN"},
  {estandar:"ODS 6.4 Uso eficiente y extraccion sostenible",disposicion:"Art. 35 inciso d",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"debil",federalismo_fit:"medio",tipo_brecha:"",nota:"Identificar acuiferos sobreexplotados y proponer acciones de recuperacion"},
  {estandar:"ODS 6.5 Gestion integrada de recursos hidricos",disposicion:"Art. 2",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"fuerte",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"fuerte",tipo_brecha:"",nota:"Concurrencia coordinada de los tres ordenes en diseno, ejecucion, seguimiento y evaluacion"},
  {estandar:"ODS 6.5 Gestion integrada de recursos hidricos",disposicion:"Art. 24",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"debil",federalismo_fit:"fuerte",tipo_brecha:"",nota:"Responsabilidad de planeacion y administracion de recursos hidricos de la Nacion"},
  {estandar:"ODS 6.5 Gestion integrada de recursos hidricos",disposicion:"Art. 29",rol_correspondencia:"contextual_habilitante",cobertura:"contextual",actor_fit:"medio",procedimiento_fit:"debil",coordinacion_fit:"medio",enforcement_fit:"no_aplica",salvaguarda_derechos_fit:"debil",federalismo_fit:"medio",tipo_brecha:"brecha_de_remision",nota:"Cinco de los ocho instrumentos de politica se remiten a la Ley de Aguas Nacionales: la operacion de la GIRH vive fuera de esta ley"},
  {estandar:"ODS 6.5 Gestion integrada de recursos hidricos",disposicion:"Arts. 30-31",rol_correspondencia:"sustantivo",cobertura:"completa",actor_fit:"fuerte",procedimiento_fit:"fuerte",coordinacion_fit:"fuerte",enforcement_fit:"medio",salvaguarda_derechos_fit:"medio",federalismo_fit:"medio",tipo_brecha:"",nota:"Estrategia Nacional Hidrica: procedimiento completo (elabora Comision+IMTA, aprueba Secretaria, publica Ejecutivo), metas a 10/20/40/60 anos, revision decenal y clausula de no regresion"},
  {estandar:"ODS 6.6 Proteccion de ecosistemas",disposicion:"Art. 23",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"fuerte",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"fuerte",tipo_brecha:"",nota:"Soluciones basadas en la naturaleza y adaptacion al cambio climatico"},
  {estandar:"ODS 6.6 Proteccion de ecosistemas",disposicion:"Art. 25 fracc. II",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"no_aplica",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"no_aplica",tipo_brecha:"",nota:"Remediacion, restauracion y proteccion de ecosistemas, cuencas y cuerpos de agua en la planeacion federal"},
  {estandar:"ODS 6.6 Proteccion de ecosistemas",disposicion:"Art. 31 fracc. XIV-XV",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"medio",procedimiento_fit:"medio",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"medio",tipo_brecha:"",nota:"Estrategia: proteger ecosistemas que sustentan la generacion de agua; adaptacion y reduccion de riesgo climatico"},
  {estandar:"ODS 6.a Cooperacion internacional",disposicion:"Art. 31 fracc. VI",rol_correspondencia:"contextual_habilitante",cobertura:"contextual",actor_fit:"medio",procedimiento_fit:"debil",coordinacion_fit:"debil",enforcement_fit:"no_aplica",salvaguarda_derechos_fit:"debil",federalismo_fit:"no_aplica",tipo_brecha:"brecha_de_cobertura",nota:"Los instrumentos internacionales solo como insumo de la Estrategia; sin mandato de cooperacion tecnica internacional"},
  {estandar:"ODS 6.b Participacion de comunidades locales",disposicion:"Arts. 37-39",rol_correspondencia:"sustantivo",cobertura:"completa",actor_fit:"fuerte",procedimiento_fit:"medio",coordinacion_fit:"fuerte",enforcement_fit:"debil",salvaguarda_derechos_fit:"fuerte",federalismo_fit:"fuerte",tipo_brecha:"",nota:"Participacion con inclusion de sectores vulnerables en planeacion, decision, ejecucion y vigilancia; obligacion de informacion oportuna y comprensible"},
  {estandar:"ODS 6.b Participacion de comunidades locales",disposicion:"Arts. 40-43",rol_correspondencia:"sustantivo",cobertura:"completa",actor_fit:"fuerte",procedimiento_fit:"medio",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"fuerte",federalismo_fit:"medio",tipo_brecha:"brecha_de_remision",nota:"Reconocimiento de sistemas comunitarios de agua; su operacion se delega a leyes estatales (42) y los indigenas/afromexicanos a la ley del art. 2o CPEUM (43)"},
  {estandar:"OG 15 / DH agua: elementos normativos",disposicion:"Art. 7",rol_correspondencia:"sustantivo",cobertura:"completa",actor_fit:"medio",procedimiento_fit:"debil",coordinacion_fit:"no_aplica",enforcement_fit:"debil",salvaguarda_derechos_fit:"fuerte",federalismo_fit:"no_aplica",tipo_brecha:"",nota:"Los seis elementos del DH al agua incorporados a nivel de estatuto"},
  {estandar:"OG 15: no discriminacion y grupos",disposicion:"Art. 6 fracc. III y X; Art. 10",rol_correspondencia:"sustantivo",cobertura:"completa",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"no_aplica",enforcement_fit:"debil",salvaguarda_derechos_fit:"fuerte",federalismo_fit:"medio",tipo_brecha:"",nota:"Universalidad, prioridad a sectores vulnerables; lista amplia: ninez, mayores, discapacidad, desplazadas, refugiadas, privadas de libertad, victimas"},
  {estandar:"OG 15: igualdad de genero",disposicion:"Art. 15",rol_correspondencia:"sustantivo",cobertura:"completa",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"fuerte",federalismo_fit:"medio",tipo_brecha:"",nota:"Paridad en gestion del agua, acciones afirmativas, proteccion de aguas de uso de mujeres"},
  {estandar:"OG 15: exigibilidad y reparacion",disposicion:"Art. 5 parr. 2",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"no_aplica",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"no_aplica",tipo_brecha:"reconocimiento_sin_garantia",nota:"Prevenir, investigar, sancionar y reparar 'en terminos de las disposiciones legales aplicables': remision sin via propia ni organo"},
  {estandar:"OG 15: interdependencia salud",disposicion:"Arts. 12-14",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"fuerte",enforcement_fit:"debil",salvaguarda_derechos_fit:"medio",federalismo_fit:"fuerte",tipo_brecha:"",nota:"Convenios de coordinacion salud-agua; vigilancia de salud publica; el verbo de los convenios es 'podran', no 'deberan'"},
  {estandar:"Progresividad presupuestal (art. 2.1 PIDESC)",disposicion:"Art. 25 fracc. III + Transitorio Tercero del Decreto",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"debil",coordinacion_fit:"medio",enforcement_fit:"debil",salvaguarda_derechos_fit:"debil",federalismo_fit:"medio",tipo_brecha:"brecha_presupuestal",nota:"Recursos 'acorde a disponibilidad presupuestaria' y transitorio que prohibe ampliaciones presupuestales: tension con la garantia progresiva"},
  {estandar:"Cadena federal: armonizacion estatal",disposicion:"Transitorio Segundo LGA",rol_correspondencia:"sustantivo",cobertura:"parcial",actor_fit:"fuerte",procedimiento_fit:"medio",coordinacion_fit:"fuerte",enforcement_fit:"debil",salvaguarda_derechos_fit:"no_aplica",federalismo_fit:"fuerte",tipo_brecha:"brecha_de_implementacion",nota:"Plazo de 180 dias para armonizacion estatal vencio el 10/jun/2026: variable trazable entidad por entidad"}
];
const expediente={ fuente_texto:'DOF', marco:'ods', nivel_revision:'validado_autora',
  descargo:'Registra correspondencia preliminar entre la Ley General de Aguas y los estándares del ODS 6, validada por la autora. No es dictamen jurídico ni evaluación de cumplimiento.',
  registros: normtraceLga34 };
function filt(list,q){ let out=list;
  if(q.q){const s=q.q.toLowerCase();out=out.filter(m=>(m.denominacion+m.tema).toLowerCase().includes(s));}
  if(q.ods) out=out.filter(m=>String(m.ods_principal)===String(q.ods));
  if(q.estatus) out=out.filter(m=>m.estatus===q.estatus);
  if(q.origen) out=out.filter(m=>m.origen===q.origen);
  return out; }

const MIME={'.html':'text/html','.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.woff2':'font/woff2','.json':'application/json','.png':'image/png','.ico':'image/x-icon','.jpg':'image/jpeg'};

export function startServer(port = 8080, distDir = DEFAULT_DIST) {
  const srv = http.createServer((req, res) => {
    const u = new URL(req.url, 'http://localhost');
    const p = decodeURIComponent(u.pathname);
    const q = Object.fromEntries(u.searchParams);
    const J = (o) => { res.writeHead(200, {'content-type':'application/json'}); res.end(JSON.stringify(o)); };
    if (p === '/huella/catalogos') return J(catalogos);
    if (p === '/huella/ejecutivo') return J(huellaEjec);
    if (p === '/huella/ejecutivo/iniciativas') return J(filt(iniciativas, q).slice(0, 60));
    if (p.startsWith('/huella/ejecutivo/iniciativas/')) return J(iniciativas[5]);
    if (p === '/minutas/') return J(minResumen);
    if (p === '/minutas/lista') return J(filt(minutas, q));
    if (p.startsWith('/normtrace/expediente/')) return J(expediente);
    if (p.startsWith('/normtrace/brief/')) return J(null);
    if (p === '/topics/') return J([]);
    let fp = normalize(join(distDir, p));
    if (fp.startsWith(distDir) && existsSync(fp) && statSync(fp).isFile()) {
      res.writeHead(200, {'content-type': MIME[extname(fp)] || 'application/octet-stream'});
      return res.end(readFileSync(fp));
    }
    res.writeHead(200, {'content-type':'text/html'});
    res.end(readFileSync(join(distDir, 'index.html')));
  });
  return new Promise((resolve) => srv.listen(port, () => resolve(srv)));
}

// Ejecutable directo: `node fixtures-server.mjs [port]`
if (import.meta.url === `file://${process.argv[1]}`) {
  const port = Number(process.argv[2] || 8080);
  startServer(port).then(() => console.log('fixtures-server en http://localhost:' + port));
}
