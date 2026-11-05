import { ref } from "vue";
import { defineStore } from "pinia";
import type { Carrera, Rol, Student } from "@/core/shared/domain/view/student.view";
import {
  entrarService,
  obtenerCarrerasService,
} from "@/core/autenticacion/infraestructure/adapters/in/service/autenticacion.service";
import { validarCodigoClaseService } from "@/core/perfil/infraestructure/adapters/in/service/perfil.service";

export interface ErroresLogin {
  alias?: string;
  carrera?: string;
  rol?: string;
  codigo?: string;
}

const LARGO_MINIMO_ALIAS = 3;

export const useCmpLoginStore = defineStore("CmpLoginStore", () => {
  const carreras = ref<Carrera[]>([]);
  const alias = ref("");
  const carrera = ref("mecatronica");
  const rol = ref<Rol | "">("estudiante");
  // Opcional: si se escribe, se valida (en el mock, contra SENS-4821).
  const codigoClase = ref("");
  const nombreClase = ref<string | null>(null);
  const errores = ref<ErroresLogin>({});
  const enviando = ref(false);

  const cargarCarreras = async () => {
    carreras.value = await obtenerCarrerasService();
  };

  const validar = (): boolean => {
    const nuevos: ErroresLogin = {};
    if (alias.value.trim().length < LARGO_MINIMO_ALIAS) {
      nuevos.alias = "Escribe un alias de 3 letras o más. No uses tu nombre real.";
    }
    if (!carrera.value) nuevos.carrera = "Elige tu carrera.";
    if (!rol.value) nuevos.rol = "Elige tu rol para continuar.";
    errores.value = nuevos;
    return Object.keys(nuevos).length === 0;
  };

  // Devuelve el estudiante si los datos son válidos; la sesión la guarda el store de sesión.
  const entrar = async (): Promise<Student | null> => {
    if (!validar() || !rol.value) return null;
    enviando.value = true;
    try {
      nombreClase.value = null;
      if (codigoClase.value.trim()) {
        const resultado = await validarCodigoClaseService(codigoClase.value);
        if (!resultado.valido) {
          errores.value = { ...errores.value, codigo: resultado.mensaje };
          return null;
        }
        nombreClase.value = resultado.nombreClase ?? null;
      }
      return await entrarService({ alias: alias.value, carrera: carrera.value, rol: rol.value });
    } finally {
      enviando.value = false;
    }
  };

  return {
    alias,
    carrera,
    carreras,
    codigoClase,
    enviando,
    errores,
    nombreClase,
    rol,
    cargarCarreras,
    entrar,
    validar,
  };
});
