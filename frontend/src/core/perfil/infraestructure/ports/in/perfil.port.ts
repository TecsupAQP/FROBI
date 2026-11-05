import type { Ajustes, Idioma } from "@/core/shared/domain/view/ajustes.view";
import type { Perfil, ResultadoCodigoClase } from "@/core/shared/domain/view/perfil.view";

export interface PerfilPort {
  obtenerPerfil(): Promise<Perfil>;
  guardarPerfil(perfil: Perfil): Promise<Perfil>;
  validarCodigoClase(codigo: string): Promise<ResultadoCodigoClase>;
  obtenerAjustes(): Promise<Ajustes>;
  guardarAjustes(ajustes: Ajustes): Promise<Ajustes>;
  obtenerIdiomas(): Promise<Idioma[]>;
}
