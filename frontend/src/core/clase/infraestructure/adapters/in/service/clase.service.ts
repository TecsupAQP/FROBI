import type { ClasePort } from "@/core/clase/infraestructure/ports/in/clase.port";
import { ClaseUseCase } from "@/core/clase/application/use-case/clase.use-case";
import type { NuevaClase, PlanGuia } from "@/core/shared/domain/view/clase.view";

const clasePort: ClasePort = new ClaseUseCase();

export const obtenerClaseService = () => clasePort.obtenerClase();
export const listarClasesService = () => clasePort.listarClases();
export const elegirClaseService = (claseId: string) => clasePort.elegirClase(claseId);
export const crearClaseService = (datos: NuevaClase) => clasePort.crearClase(datos);
export const invitarService = (aliasOCorreo: string) => clasePort.invitar(aliasOCorreo);
export const obtenerDetalleAlumnoService = (alias: string) => clasePort.obtenerDetalleAlumno(alias);
export const salirDeClaseService = () => clasePort.salirDeClase();
export const listarMaterialesClaseService = () => clasePort.listarMateriales();
export const subirMaterialClaseService = (archivo: File, plan: PlanGuia) =>
  clasePort.subirMaterial(archivo, plan);
export const guardarPlanGuiaService = (materialId: string, plan: PlanGuia) =>
  clasePort.guardarPlan(materialId, plan);
export const miAvanceGuiasService = () => clasePort.miAvance();
export const avanceGuiasClaseService = () => clasePort.avanceClase();
