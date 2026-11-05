// La API no respondió (sin red o servidor caído): las pantallas muestran "Sin conexión".
export class SinConexionError extends Error {
  constructor() {
    super("Sin conexión");
    this.name = "SinConexionError";
  }
}
