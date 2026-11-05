/// <reference types="vite/client" />

interface ImportMetaEnv {
  // URL base de la API, con el prefijo /api/v1. Por defecto http://localhost:8000/api/v1.
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
