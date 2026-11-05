import type { ClasePort } from "@/core/clase/infraestructure/ports/in/clase.port";
import { ClaseUseCase } from "@/core/clase/application/use-case/clase.use-case";
import type { NuevaClase } from "@/core/shared/domain/view/clase.view";

const clasePort: ClasePort = new ClaseUseCase();

export const obtenerClaseService = () => clasePort.obtenerClase();
export const obtenerMaterialesClaseService = () => clasePort.obtenerMateriales();
export const crearClaseService = (datos: NuevaClase) => clasePort.crearClase(datos);
export const invitarPorCorreoService = (correo: string) => clasePort.invitarPorCorreo(correo);
export const obtenerDetalleAlumnoService = (alias: string) => clasePort.obtenerDetalleAlumno(alias);
export const salirDeClaseService = () => clasePort.salirDeClase();
