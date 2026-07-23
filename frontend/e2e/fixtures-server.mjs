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
const expediente={ registros:[
  {estandar:'PIDESC art. 11', disposicion:'LGA art. 4', rol_correspondencia:'sustantivo', cobertura:'parcial'},
  {estandar:'Observación Gral. 15', disposicion:'LGA art. 7', rol_correspondencia:'sustantivo', cobertura:'alta'},
  {estandar:'ODS 6.1', disposicion:'LGA art. 12', rol_correspondencia:'contextual', cobertura:'media'},
]};
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
