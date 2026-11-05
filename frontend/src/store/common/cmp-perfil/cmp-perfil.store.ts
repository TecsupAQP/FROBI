import { ref } from "vue";
import { defineStore } from "pinia";
import type {
  ConfiguradoPor,
  ModoUso,
  Perfil,
  PerfilAccesibilidadId,
  ResultadoCodigoClase,
} from "@/core/shared/domain/view/perfil.view";
import {
  guardarPerfilService,
  obtenerPerfilService,
  validarCodigoClaseService,
} from "@/core/perfil/infraestructure/adapters/in/service/perfil.service";
import { PERFIL_INICIAL } from "@/mocks/perfil.mock";

// Rol, perfiles de accesibilidad (varios a la vez), quién configuró y qué pasos ya vio.
export const useCmpPerfilStore = defineStore("CmpPerfilStore", () => {
  const perfil = ref<Perfil>(structuredClone(PERFIL_INICIAL));
  const cargado = ref(false);
  const guardando = ref(false);

  const cargar = async () => {
    if (cargado.value) return;
    perfil.value = await obtenerPerfilService();
    cargado.value = true;
  };

  const guardar = async () => {
    guardando.value = true;
    try {
      perfil.value = await guardarPerfilService(perfil.value);
    } finally {
      guardando.value = false;
    }
  };

  const elegirModo = (modo: ModoUso) => {
    perfil.value.modo = modo;
    if (modo !== "estudiante-clase") perfil.value.codigoClase = null;
  };

  const validarCodigo = async (codigo: string): Promise<ResultadoCodigoClase> => {
    const resultado = await validarCodigoClaseService(codigo);
    if (resultado.valido) perfil.value.codigoClase = codigo.trim().toUpperCase();
    return resultado;
  };

  const alternarPerfil = (id: PerfilAccesibilidadId) => {
    const actuales = perfil.value.perfiles;
    perfil.value.perfiles = actuales.includes(id)
      ? actuales.filter((item) => item !== id)
      : [...actuales, id];
  };

  const elegirConfiguradoPor = (quien: ConfiguradoPor) => {
    perfil.value.configuradoPor = quien;
  };

  const marcarIntroVista = () => {
    perfil.value.vioIntro = true;
    return guardar();
  };

  const marcarAsistenteVisto = () => {
    perfil.value.vioAsistente = true;
    return guardar();
  };

  const reiniciarAsistente = () => {
    perfil.value.vioAsistente = false;
    return guardar();
  };

  return {
    cargado,
    guardando,
    perfil,

    alternarPerfil,
    cargar,
    elegirConfiguradoPor,
    elegirModo,
    guardar,
    marcarAsistenteVisto,
    marcarIntroVista,
    reiniciarAsistente,
    validarCodigo,
  };
});
