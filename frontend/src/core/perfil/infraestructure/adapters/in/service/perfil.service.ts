import type { PerfilPort } from "@/core/perfil/infraestructure/ports/in/perfil.port";
import { PerfilUseCase } from "@/core/perfil/application/use-case/perfil.use-case";
import type { Ajustes } from "@/core/shared/domain/view/ajustes.view";
import type { Perfil } from "@/core/shared/domain/view/perfil.view";

const perfilPort: PerfilPort = new PerfilUseCase();

export const obtenerPerfilService = () => perfilPort.obtenerPerfil();
export const guardarPerfilService = (perfil: Perfil) => perfilPort.guardarPerfil(perfil);
export const validarCodigoClaseService = (codigo: string) => perfilPort.validarCodigoClase(codigo);
export const obtenerAjustesService = () => perfilPort.obtenerAjustes();
export const guardarAjustesService = (ajustes: Ajustes) => perfilPort.guardarAjustes(ajustes);
export const obtenerIdiomasService = () => perfilPort.obtenerIdiomas();
