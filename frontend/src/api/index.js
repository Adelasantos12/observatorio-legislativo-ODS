import config from '@/config';
import axios from 'axios';

const kb = config.KNOWLEDGEBASE;
const params = {
  knowledgebase: kb,
};

export default {
  getTopics() {
    return axios.get(getEndpoint()).then((response) => response.data);

    function getEndpoint() {
      return [config.URL, '/topics/'].join('');
    }
  },
  getTopic(topicId) {
    return axios.get(getEndpoint(topicId)).then((response) => response.data);

    function getEndpoint(topicId) {
      return [config.URL, '/topics/', topicId].join('');
    }
  },
  getTags(topicId) {
    return axios
      .get(getEndpoint(topicId))
      .then((response) => response.data.tags);

    function getEndpoint(topicId) {
      return [config.URL, '/topics/', topicId].join('');
    }
  },
  annotate(text, file, deep = false) {
    let formData = new FormData();
    formData.append('text', text);
    formData.append('file', file);
    formData.append('knowledgebase', kb);
    if (deep) {
      // Etapa 2 (segmentación) + etapa 3 (codificación NormTrace asíncrona).
      formData.append('segment', 'legal');
      formData.append('deep', 'true');
    }

    return axios.post(getEndpoint(), formData);

    function getEndpoint() {
      return [config.URL, '/tagger/'].join('');
    }
  },
  getScannerResult(taskID) {
    return axios.get(getEndpoint(taskID), { params });

    function getEndpoint(taskID) {
      return [config.URL, '/tagger/result/', taskID].join('');
    }
  },
  getNormtraceResult(taskID) {
    // Bloque `structural` de la codificación NormTrace (etapa 3).
    return axios.get(getEndpoint(taskID));

    function getEndpoint(taskID) {
      return [config.URL, '/tagger/deep/', taskID].join('');
    }
  },
  saveScanned(title, expiration, excerpt, result) {
    return axios.post(getEndpoint(), {
      title,
      expiration,
      excerpt,
      result: JSON.stringify(result),
      verified: false,
    });

    function getEndpoint() {
      return [config.URL, '/scanned/'].join('');
    }
  },
  getScanned(scannedId) {
    return axios
      .get(getEndpoint(scannedId))
      .then((response) => response.data)
      .catch((error) => {
        console.log(error.response);
      });

    function getEndpoint(scannedId) {
      return [config.URL, '/scanned/', scannedId].join('');
    }
  },
  searchScanned(query) {
    return axios
      .get(getEndpoint(query))
      .then((response) => response.data)
      .catch((error) => {
        console.log(error.response);
      });

    function getEndpoint(query) {
      return [config.URL, '/scanned/search/', query].join('');
    }
  },

  // --- Huella 2030 (fase H) ---
  getHuellaCatalogos() {
    return axios
      .get([config.URL, '/huella/catalogos'].join(''))
      .then((r) => r.data);
  },
  getHuellaEjecutivo() {
    return axios
      .get([config.URL, '/huella/ejecutivo'].join(''))
      .then((r) => r.data);
  },
  getHuellaIniciativas(params = {}) {
    return axios
      .get([config.URL, '/huella/ejecutivo/iniciativas'].join(''), { params })
      .then((r) => r.data);
  },
  getHuellaIniciativa(id) {
    return axios
      .get([config.URL, '/huella/ejecutivo/iniciativas/', id].join(''))
      .then((r) => r.data);
  },
};
