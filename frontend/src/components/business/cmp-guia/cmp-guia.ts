import { defineComponent, onMounted } from "vue";
import { useRouter } from "vue-router";
import VCardFormato from "@/components/base/v-card-formato/v-card-formato.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import CmpDocumentoOriginal from "@/components/business/cmp-guia/content/cmp-documento-original/cmp-documento-original.vue";
import useCmpGuia from "@/composables/business/cmp-guia/cmp-guia.composable";
import { FORMATOS } from "@/constants/formatos.constant";
import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpGuia",
  components: { VCardFormato, VCargando, CmpDocumentoOriginal, CmpEncabezadoPagina },
  setup() {
    const PREFIX = "cmp-guia";

    const router = useRouter();

    const {
      documentoAbierto,
      documentoError,
      documentoUrl,
      formatoAdaptando,
      guia,
      tardaMucho,
      adaptar,
      alternarDocumento,
      cargarGuia,
    } = useCmpGuia();

    const nombreFormato = (id: FormatoId) => FORMATOS.find((formato) => formato.id === id)?.nombre ?? "";

    const elegirFormato = async (formato: FormatoId) => {
      if (formatoAdaptando.value) return;
      await adaptar(formato);
      router.push({ name: RutaEnum.RESULTADO, params: { formato } });
    };

    // Un PDF se muestra abierto: es el material tal como lo subió la persona.
    onMounted(async () => {
      await cargarGuia();
      if (guia.value?.tieneArchivo && !documentoAbierto.value) await alternarDocumento();
    });

    return {
      FORMATOS,
      PREFIX,
      documentoAbierto,
      documentoError,
      documentoUrl,
      alternarDocumento,
      formatoAdaptando,
      guia,
      tardaMucho,
      nombreFormato,
      elegirFormato,
    };
  },
});
