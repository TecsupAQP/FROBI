import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { Rol, SesionIniciada, Student } from "@/core/shared/domain/view/student.view";
import {
  cambiarAliasService,
  entrarService,
  salirService,
} from "@/core/autenticacion/infraestructure/adapters/in/service/autenticacion.service";
import { guardarToken, leerToken } from "@/core/shared/infraestructure/http/api.client";
import { olvidarContextoEstudio } from "@/core/shared/infraestructure/http/contexto-estudio";
import { useCmpAjustesStore } from "@/store/common/cmp-ajustes/cmp-ajustes.store";
import { useCmpClaseStore } from "@/store/common/cmp-clase/cmp-clase.store";
import { useCmpPerfilStore } from "@/store/common/cmp-perfil/cmp-perfil.store";

const CLAVE_ALMACEN = "frobi-sesion";

const leerSesionGuardada = (): SesionIniciada | null => {
  if (!leerToken()) return null;
  try {
    const guardada = localStorage.getItem(CLAVE_ALMACEN);
    return guardada ? (JSON.parse(guardada) as SesionIniciada) : null;
  } catch {
    return null;
  }
};

const escribir = (sesion: SesionIniciada | null) => {
  try {
    if (sesion) localStorage.setItem(CLAVE_ALMACEN, JSON.stringify(sesion));
    else localStorage.removeItem(CLAVE_ALMACEN);
  } catch {
    // Sin almacenamiento disponible: la sesión vive solo en memoria.
  }
};

// Datos que pertenecen a una persona: se olvidan cuando entra otra.
const olvidarDatosDeLaPersona = () => {
  try {
    localStorage.removeItem("frobi-perfil-local");
    localStorage.removeItem("frobi-clase-id");
  } catch {
    // Nada que limpiar.
  }
  olvidarContextoEstudio();
  useCmpPerfilStore().reiniciar();
  useCmpAjustesStore().reiniciar();
  useCmpClaseStore().reiniciar();
};

// Sesión con la API: token en localStorage (lo maneja el cliente HTTP) y datos de la persona.
export const useCmpSesionStore = defineStore("CmpSesionStore", () => {
  const sesion = ref<SesionIniciada | null>(leerSesionGuardada());

  const estudiante = computed<Student | null>(() => sesion.value?.estudiante ?? null);
  const clase = computed(() => sesion.value?.clase ?? null);
  const personaId = computed(() => sesion.value?.personaId ?? null);
  const haIniciado = computed(() => sesion.value !== null);
  const esDocente = computed(() => estudiante.value?.rol === "docente");
  const inicial = computed(() => estudiante.value?.alias.charAt(0).toUpperCase() ?? "");

  const iniciarSesion = (nueva: SesionIniciada) => {
    if (sesion.value?.personaId !== nueva.personaId) olvidarDatosDeLaPersona();
    sesion.value = nueva;
    escribir(nueva);
  };

  // Olvida la sesión local (por ejemplo, cuando la API responde 401).
  const olvidarSesion = () => {
    sesion.value = null;
    escribir(null);
    guardarToken(null);
    olvidarDatosDeLaPersona();
  };

  const cerrarSesion = async () => {
    try {
      await salirService();
    } finally {
      olvidarSesion();
    }
  };

  const cambiarAlias = async (alias: string) => {
    if (!sesion.value) return;
    const estudianteNuevo = await cambiarAliasService(alias);
    iniciarSesion({ ...sesion.value, estudiante: estudianteNuevo });
  };

  // El rol se fija al entrar: cambiarlo abre una sesión nueva con el mismo alias y carrera.
  const cambiarRol = async (rol: Rol) => {
    if (!sesion.value || sesion.value.estudiante.rol === rol) return;
    iniciarSesion(await entrarService({ ...sesion.value.estudiante, rol }));
  };

  const actualizarClase = (nueva: SesionIniciada["clase"]) => {
    if (!sesion.value) return;
    iniciarSesion({ ...sesion.value, clase: nueva });
  };

  return {
    clase,
    personaId,
    estudiante,
    haIniciado,
    esDocente,
    inicial,
    actualizarClase,
    cambiarAlias,
    cambiarRol,
    cerrarSesion,
    iniciarSesion,
    olvidarSesion,
  };
});
