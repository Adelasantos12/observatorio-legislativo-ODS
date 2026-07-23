export default {
  SHORTNAME: import.meta.env.VITE_VUE_APP_SHORTNAME || 'escaner-mx',
  URL: import.meta.env.VITE_VUE_APP_BACKEND_URL || 'http://localhost:8080',
  USE_ALERTS: import.meta.env.VITE_VUE_APP_USE_ALERTS || false,
  KNOWLEDGEBASE: import.meta.env.VITE_KNOWLEDGEBASE || 'ods',
  DEFAULT_LOCALE: import.meta.env.VITE_DEFAULT_LOCALE || 'es',
  MENU: {
    es: [
      {
        route: 'huella',
        name: 'Huella 2030',
        condition: true,
      },
      {
        route: 'minutas',
        name: 'Minutas',
        condition: true,
      },
      {
        route: 'scanner',
        name: 'Escáner',
        condition: true,
      },
      {
        route: 'metodologia',
        name: 'Metodología',
        condition: true,
      },
      {
        route: 'about',
        name: 'Acerca',
        condition: true,
      },
    ],
    en: [
      {
        route: 'huella',
        name: 'Huella 2030',
        condition: true,
      },
      {
        route: 'minutas',
        name: 'Minutas',
        condition: true,
      },
      {
        route: 'scanner',
        name: 'Scanner',
        condition: true,
      },
      {
        route: 'about',
        name: 'About',
        condition: true,
      },
    ],
  },
  DISCLAIMER: {
    es: {
      name: '',
    },
    en: {
      route: '',
      name: 'This is a beta version with a limited knowledge base for now',
      external: false,
    },
  },
  // Logo PLACEHOLDER textual del despliegue mexicano (SVG con el nombre de
  // marca). Sustituir por el arte definitivo cuando esté disponible (fase F1).
  // Isotipo del sitio: el anillo de los 17 ODS (Nota v6.1). El header y el pie
  // usan el lockup vivo (BrandLockup); esta clave queda para metadatos/compat.
  LOGO: '/img/anillo-ods.svg',

  DEFAULT_PAGE_TITLE: {
    es: 'Escáner Legislativo MX — Escanea cualquier texto legislativo en clave ODS',
    en: 'Escáner Legislativo MX — Scan any Mexican legislative text against the 2030 Agenda',
  },
  DEFAULT_METATAGS: {
    es: [
      {
        name: 'description',
        content:
          'Escáner Legislativo MX etiqueta y visualiza en segundos cualquier texto legislativo mexicano en clave de Agenda 2030 y sus Objetivos de Desarrollo Sostenible (ODS), y traza su relación con marcos jurídicos e internacionales.',
      },
      {
        name: 'keywords',
        content:
          'Agenda 2030, ODS, Objetivos de Desarrollo Sostenible, legislación mexicana, Cámara de Diputados, Congreso de la Unión, DOF, iniciativa, dictamen',
      },
      {
        itemprop: 'image',
        content: '/img/og-anillo-ods.svg',
      },
      {
        name: 'twitter:card',
        content: 'summary_large_image',
      },
      {
        name: 'twitter:title',
        content: 'Escáner Legislativo MX',
      },
      {
        name: 'twitter:description',
        content:
          'Etiqueta y visualiza cualquier texto legislativo mexicano en clave de Agenda 2030 y traza su relación con marcos jurídicos e internacionales.',
      },
      {
        property: 'og:title',
        content: 'Escáner Legislativo MX',
      },
      {
        property: 'og:type',
        content: 'website',
      },
      {
        property: 'og:image',
        content: '/img/og-anillo-ods.svg',
      },
      {
        property: 'og:description',
        content:
          'Etiqueta y visualiza cualquier texto legislativo mexicano en clave de Agenda 2030 y traza su relación con marcos jurídicos e internacionales.',
      },
      {
        property: 'og:site_name',
        content: 'Escáner Legislativo MX',
      },
    ],
    en: [
      {
        name: 'description',
        content:
          'Escáner Legislativo MX tags and visualises any Mexican legislative text against the 2030 Agenda and its Sustainable Development Goals, and traces its relation to legal and international frameworks.',
      },
      {
        name: 'keywords',
        content:
          '2030 Agenda, SDG, Sustainable Development Goals, Mexican legislation, Chamber of Deputies, Congress of the Union, DOF, bill',
      },
      {
        itemprop: 'image',
        content: '/img/og-anillo-ods.svg',
      },
      {
        name: 'twitter:card',
        content: 'summary_large_image',
      },
      {
        name: 'twitter:title',
        content: 'Escáner Legislativo MX',
      },
      {
        name: 'twitter:description',
        content:
          'Tag and visualise any Mexican legislative text against the 2030 Agenda and trace its relation to legal and international frameworks.',
      },
      {
        property: 'og:title',
        content: 'Escáner Legislativo MX',
      },
      {
        property: 'og:type',
        content: 'website',
      },
      {
        property: 'og:image',
        content: '/img/og-anillo-ods.svg',
      },
      {
        property: 'og:description',
        content:
          'Tag and visualise any Mexican legislative text against the 2030 Agenda and trace its relation to legal and international frameworks.',
      },
      {
        property: 'og:site_name',
        content: 'Escáner Legislativo MX',
      },
    ],
  },
  STYLES: {
    es: {
      topics: {
        'ODS 1 Fin de la pobreza': {
          shortname: 'ODS 1',
          color: '#eb1c2d',
          image: 'ods-1.svg',
        },
        'ODS 2 Hambre cero': {
          shortname: 'ODS 2',
          color: '#d3a029',
          image: 'ods-2.svg',
        },
        'ODS 3 Salud y bienestar': {
          shortname: 'ODS 3',
          color: '#4c9f38',
          image: 'ods-3.svg',
        },
        'ODS 4 Educación de calidad': {
          shortname: 'ODS 4',
          color: '#c52333',
          image: 'ods-4.svg',
        },
        'ODS 5 Igualdad de género': {
          shortname: 'ODS 5',
          color: '#ed4135',
          image: 'ods-5.svg',
        },
        'ODS 6 Agua limpia y saneamiento': {
          shortname: 'ODS 6',
          color: '#00aed9',
          image: 'ods-6.svg',
        },
        'ODS 7 Energía asequible y no contaminante': {
          shortname: 'ODS 7',
          color: '#fdb713',
          image: 'ods-7.svg',
        },
        'ODS 8 Trabajo decente y crecimiento económico': {
          shortname: 'ODS 8',
          color: '#8f1838',
          image: 'ods-8.svg',
        },
        'ODS 9 Industria, innovación e infraestructura': {
          shortname: 'ODS 9',
          color: '#f06a38',
          image: 'ods-9.svg',
        },
        'ODS 10 Reducción de las desigualdades': {
          shortname: 'ODS 10',
          color: '#dd1367',
          image: 'ods-10.svg',
        },
        'ODS 11 Ciudades y comunidades sostenibles': {
          shortname: 'ODS 11',
          color: '#f69c39',
          image: 'ods-11.svg',
        },
        'ODS 12 Producción y consumo responsables': {
          shortname: 'ODS 12',
          color: '#cf8d2a',
          image: 'ods-12.svg',
        },
        'ODS 13 Acción por el clima': {
          shortname: 'ODS 13',
          color: '#48773e',
          image: 'ods-13.svg',
        },
        'ODS 14 Vida submarina': {
          shortname: 'ODS 14',
          color: '#007dbc',
          image: 'ods-14.svg',
        },
        'ODS 15 Vida de ecosistemas terrestres': {
          shortname: 'ODS 15',
          color: '#5cb84d',
          image: 'ods-15.svg',
        },
        'ODS 16 Paz, justicia e instituciones sólidas': {
          shortname: 'ODS 16',
          color: '#02558b',
          image: 'ods-16.svg',
        },
        'ODS 17 Alianzas para lograr los objetivos': {
          shortname: 'ODS 17',
          color: '#183668',
          image: 'ods-17.svg',
        },
        'no-topic': {
          shortname: 'Sin relación con la Agenda2030',
        },
      },
      subtopics: {
        '1.1 Erradicar la pobreza extrema': {
          color: '#eb1c2d',
          image: 'ods-01.svg',
        },
        '1.2 Niveles nacionales de pobreza': {
          color: '#eb1c2d',
          image: 'ods-01.svg',
        },
      },
      defaultColor: '#cecece',
      defaultImage: 'placeholder.png',
    },
    en: {
      topics: {
        'SDG 1 No Poverty': {
          shortname: 'SDG 1',
          color: '#eb1c2d',
          image: 'ods-1.svg',
        },
        'SDG 2 Zero Hunger': {
          shortname: 'SDG 2',
          color: '#d3a029',
          image: 'ods-2.svg',
        },
        'SDG 3 Good Health and Well-Being': {
          shortname: 'SDG 3',
          color: '#4c9f38',
          image: 'ods-3.svg',
        },
        'SDG 4 Quality Education': {
          shortname: 'SDG 4',
          color: '#c52333',
          image: 'ods-4.svg',
        },
        'SDG 5 Gender Equality': {
          shortname: 'SDG 5',
          color: '#ed4135',
          image: 'ods-5.svg',
        },
        'SDG 6 Clean Water and Sanitation': {
          shortname: 'SDG 6',
          color: '#00aed9',
          image: 'ods-6.svg',
        },
        'SDG 7 Affordable and Clean Energy': {
          shortname: 'SDG 7',
          color: '#fdb713',
          image: 'ods-7.svg',
        },
        'SDG 8 Decent Work and Economic Growth': {
          shortname: 'SDG 8',
          color: '#8f1838',
          image: 'ods-8.svg',
        },
        'SDG 9 Industry, Innovation and Infraestructure': {
          shortname: 'SDG 9',
          color: '#f06a38',
          image: 'ods-9.svg',
        },
        'SDG 10 Reduced Inequalities': {
          shortname: 'SDG 10',
          color: '#dd1367',
          image: 'ods-10.svg',
        },
        'SDG 11 Sustainable Cities and Communities': {
          shortname: 'SDG 11',
          color: '#f69c39',
          image: 'ods-11.svg',
        },
        'SDG 12 Sustainable Production and Consumption': {
          shortname: 'SDG 12',
          color: '#cf8d2a',
          image: 'ods-12.svg',
        },
        'SDG 13 Climate Action': {
          shortname: 'SDG 13',
          color: '#48773e',
          image: 'ods-13.svg',
        },
        'SDG 14 Life Below Water': {
          shortname: 'SDG 14',
          color: '#007dbc',
          image: 'ods-14.svg',
        },
        'SDG 15 Life on Land': {
          shortname: 'SDG 15',
          color: '#5cb84d',
          image: 'ods-15.svg',
        },
        'SDG 16 Peace, Justice and Strong Institutions': {
          shortname: 'SDG 16',
          color: '#02558b',
          image: 'ods-16.svg',
        },
        'SDG 17 Partnerships for the Goals': {
          shortname: 'SDG 17',
          color: '#183668',
          image: 'ods-17.svg',
        },
        'no-topic': {
          shortname: 'Unlinked with the 2030 Agenda',
        },
      },
      subtopics: {
        '1.1 Erradicar la pobreza extrema': {
          color: '#eb1c2d',
          image: 'ods-01.svg',
        },
        '1.2 Niveles nacionales de pobreza': {
          color: '#eb1c2d',
          image: 'ods-01.svg',
        },
      },
      defaultColor: '#cecece',
      defaultImage: 'placeholder.png',
    },
  },
};
