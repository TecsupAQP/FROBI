import { ref } from "vue";
import { defineStore } from "pinia";
import type { Material } from "@/core/shared/domain/view/material.view";
import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";
import {
  enlaceDocumentoService,
  obtenerGuiaService,
} from "@/core/material/infraestructure/adapters/in/service/material.service";
import { useCmpResultadoStore } from "@/store/business/cmp-resultado/cmp-resultado.store";

// RNF06: si la adaptación tarda más de 15 s, se avisa que se usará una respuesta de ejemplo.
const ESPERA_RESPALDO_MS = 15000;

export const useCmpGuiaStore = defineStore("CmpGuiaStore", () => {
  const guia = ref<Material | null>(null);
  const temaAbierto = ref<string | null>("tema-1");
  const formatoAdaptando = ref<FormatoId | null>(null);
  const tardaMucho = ref(false);
  // Vista previa del PDF original: el enlace firmado vence, así que se pide cada vez que se abre.
  const documentoAbierto = ref(false);
  const documentoUrl = ref<string | null>(null);
  const documentoError = ref(false);

  const cargarGuia = async () => {
    documentoAbierto.value = false;
    documentoUrl.value = null;
    guia.value = await obtenerGuiaService();
  };

  const alternarDocumento = async () => {
    documentoAbierto.value = !documentoAbierto.value;
    if (!documentoAbierto.value || !guia.value) return;
    documentoUrl.value = null;
    documentoError.value = false;
    try {
      documentoUrl.value = await enlaceDocumentoService(guia.value.id);
    } catch {
      documentoError.value = true;
    }
  };

  const alternarTema = (temaId: string) => {
    temaAbierto.value = temaAbierto.value === temaId ? null : temaId;
  };

  // Prepara la adaptación antes de ir a V3, para que el resultado aparezca sin otra espera.
  const adaptar = async (formato: FormatoId): Promise<string> => {
    const temaId = temaAbierto.value ?? guia.value?.temas[0]?.id ?? "tema-1";
    formatoAdaptando.value = formato;
    tardaMucho.value = false;
    const aviso = window.setTimeout(() => (tardaMucho.value = true), ESPERA_RESPALDO_MS);
    try {
      await useCmpResultadoStore().cargarAdaptacion(temaId, formato);
      return temaId;
    } finally {
      window.clearTimeout(aviso);
      formatoAdaptando.value = null;
    }
  };

  return {
    documentoAbierto,
    documentoError,
    documentoUrl,
    formatoAdaptando,
    guia,
    tardaMucho,
    temaAbierto,
    adaptar,
    alternarDocumento,
    alternarTema,
    cargarGuia,
  };
});
