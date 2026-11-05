import { ref } from "vue";
import { defineStore } from "pinia";
import type { Carrera, Rol, SesionIniciada } from "@/core/shared/domain/view/student.view";
import {
  entrarService,
  obtenerCarrerasService,
} from "@/core/autenticacion/infraestructure/adapters/in/service/autenticacion.service";
import { CodigoClaseInvalidoError } from "@/core/autenticacion/infraestructure/ports/in/autenticacion.port";

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
  // Opcional: si se escribe, la API lo valida al entrar.
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

  // Abre la sesión en la API. Un código de clase inválido no deja entrar: se avisa en su campo.
  const entrar = async (): Promise<SesionIniciada | null> => {
    if (!validar() || !rol.value) return null;
    enviando.value = true;
    try {
      const sesion = await entrarService(
        { alias: alias.value, carrera: carrera.value, rol: rol.value },
        codigoClase.value,
      );
      nombreClase.value = sesion.clase?.nombre ?? null;
      return sesion;
    } catch (error) {
      if (error instanceof CodigoClaseInvalidoError) {
        errores.value = { ...errores.value, codigo: error.message };
        return null;
      }
      errores.value = {
        ...errores.value,
        alias: "No pudimos entrar. Revisa tu conexión e inténtalo de nuevo.",
      };
      return null;
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
