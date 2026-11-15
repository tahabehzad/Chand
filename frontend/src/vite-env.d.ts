/// <reference types="vite/client" />

interface ImportMetaEnv {
  /**
   * Origin of the FastAPI service. Defaults to the same origin when unset.
   * No other variable is read by the client: secrets must never reach the bundle.
   */
  readonly VITE_API_BASE_URL?: string;
  readonly DEV: boolean;
  readonly PROD: boolean;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
