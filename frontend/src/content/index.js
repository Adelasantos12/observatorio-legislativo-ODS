// Acceso al texto visible (adenda v4). Todo el copy vive en es.json; los
// componentes lo consumen por clave y rellenan los {tokens} con cifras vivas.
import es from './es.json';

export const content = es;

// Interpola {token} en una cadena con valores del objeto `vars`.
export function fill(str, vars = {}) {
  if (typeof str !== 'string') return str;
  return str.replace(/\{(\w+)\}/g, (_, k) => (vars[k] != null ? vars[k] : ''));
}

export default content;
