import type { PerfilPort } from "@/core/perfil/infraestructure/ports/in/perfil.port";
import type { Ajustes, Idioma } from "@/core/shared/domain/view/ajustes.view";
import type { Perfil, ResultadoCodigoClase } from "@/core/shared/domain/view/perfil.view";
import { respuestaSimulada } from "@/core/shared/application/util/simulacion.util";
import {
  AJUSTES_INICIALES,
  CODIGO_CLASE_EJEMPLO,
  IDIOMAS_MOCK,
  NOMBRE_CLASE_EJEMPLO,
  PERFIL_INICIAL,
} from "@/mocks/perfil.mock";

const CLAVE_PERFIL = "frobi-perfil";
const CLAVE_AJUSTES = "frobi-ajustes";

// En la maqueta el "backend" es localStorage; si no está disponible se usan los valores iniciales.
function leer<T extends object>(clave: string, inicial: T): T {
  try {
    const guardado = localStorage.getItem(clave);
    return guardado ? { ...inicial, ...(JSON.parse(guardado) as Partial<T>) } : inicial;
  } catch {
    return inicial;
  }
}

function escribir<T>(clave: string, valor: T): void {
  try {
    localStorage.setItem(clave, JSON.stringify(valor));
  } catch {
    // Sin almacenamiento: el valor vive solo en memoria.
  }
}

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class PerfilUseCase implements PerfilPort {
  obtenerPerfil(): Promise<Perfil> {
    return respuestaSimulada(leer(CLAVE_PERFIL, PERFIL_INICIAL), 300);
  }

  guardarPerfil(perfil: Perfil): Promise<Perfil> {
    escribir(CLAVE_PERFIL, perfil);
    return respuestaSimulada(perfil, 400);
  }

  validarCodigoClase(codigo: string): Promise<ResultadoCodigoClase> {
    const valido = codigo.trim().toUpperCase() === CODIGO_CLASE_EJEMPLO;
    return respuestaSimulada(
      valido
        ? { valido, nombreClase: NOMBRE_CLASE_EJEMPLO }
        : { valido, mensaje: "No encontramos esa clase. Revisa el código con tu docente." },
      500,
    );
  }

  obtenerAjustes(): Promise<Ajustes> {
    return respuestaSimulada(leer(CLAVE_AJUSTES, AJUSTES_INICIALES), 300);
  }

  guardarAjustes(ajustes: Ajustes): Promise<Ajustes> {
    escribir(CLAVE_AJUSTES, ajustes);
    return respuestaSimulada(ajustes, 300);
  }

  obtenerIdiomas(): Promise<Idioma[]> {
    return respuestaSimulada(IDIOMAS_MOCK, 300);
  }
}
