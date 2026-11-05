import { computed, defineComponent, onMounted } from "vue";
import { useRouter } from "vue-router";
import VCardFormato from "@/components/base/v-card-formato/v-card-formato.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import CmpDocumentoOriginal from "@/components/business/cmp-guia/content/cmp-documento-original/cmp-documento-original.vue";
import CmpTema from "@/components/business/cmp-guia/content/cmp-tema/cmp-tema.vue";
import useCmpGuia from "@/composables/business/cmp-guia/cmp-guia.composable";
import { FORMATOS } from "@/constants/formatos.constant";
import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpGuia",
  components: { VCardFormato, VCargando, CmpDocumentoOriginal, CmpEncabezadoPagina, CmpTema },
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
      temaAbierto,
      adaptar,
      alternarDocumento,
      alternarTema,
      cargarGuia,
    } = useCmpGuia();

    const temaActual = computed(
      () => guia.value?.temas.find((tema) => tema.id === temaAbierto.value) ?? guia.value?.temas[0],
    );

    const nombreFormato = (id: FormatoId) => FORMATOS.find((formato) => formato.id === id)?.nombre ?? "";

    const elegirFormato = async (formato: FormatoId) => {
      if (formatoAdaptando.value) return;
      await adaptar(formato);
      router.push({ name: RutaEnum.RESULTADO, params: { formato } });
    };

    onMounted(cargarGuia);

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
      temaAbierto,
      alternarTema,
      temaActual,
      nombreFormato,
      elegirFormato,
    };
  },
});
