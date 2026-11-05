// La API no respondió (sin red o servidor caído): las pantallas muestran "Sin conexión".
export class SinConexionError extends Error {
  constructor() {
    super("Sin conexión");
    this.name = "SinConexionError";
  }
}

// La persona todavía no subió ni eligió una guía: las pantallas de estudio la piden primero.
export class SinGuiaError extends Error {
  constructor() {
    super("Todavía no tienes una guía");
    this.name = "SinGuiaError";
  }
}
