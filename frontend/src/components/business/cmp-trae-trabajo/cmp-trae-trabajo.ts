import { defineComponent, onMounted } from "vue";
import { useRouter } from "vue-router";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VField from "@/components/base/v-field/v-field.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import CmpSubirPdf from "@/components/business/cmp-inicio/modals/cmp-subir-pdf/cmp-subir-pdf.vue";
import CmpPasosSiguientes from "@/components/business/cmp-trae-trabajo/content/cmp-pasos-siguientes/cmp-pasos-siguientes.vue";
import useCmpInicio from "@/composables/business/cmp-inicio/cmp-inicio.composable";
import useCmpTrabajo from "@/composables/business/cmp-trabajo/cmp-trabajo.composable";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpTraeTrabajo",
  components: { VButton, VCargando, VField, VIcon, CmpEncabezadoPagina, CmpSubirPdf, CmpPasosSiguientes },
  setup() {
    const PREFIX = "cmp-trae-trabajo";

    const router = useRouter();

    const { borrador, consigna, palabras, puedeRevisar, revisando, cargarEjemplo, revisar } = useCmpTrabajo();

    // El modal de subida es el mismo de Inicio.
    const {
      archivo,
      fase,
      modalAbierto,
      nombreArchivo,
      progreso,
      tamanoArchivoMb,
      abrirModal,
      cancelarSubida,
      cerrarModal,
      elegirArchivo,
    } = useCmpInicio();

    const revisarYContinuar = async () => {
      await revisar();
      router.push({ name: RutaEnum.REVISION });
    };

    const usarPdf = () => {
      if (archivo.value) borrador.value = archivo.value.vistaPrevia.texto;
      cerrarModal();
    };

    onMounted(cargarEjemplo);

    return {
      PREFIX,
      borrador,
      consigna,
      palabras,
      puedeRevisar,
      revisando,
      archivo,
      fase,
      modalAbierto,
      nombreArchivo,
      progreso,
      tamanoArchivoMb,
      abrirModal,
      cancelarSubida,
      elegirArchivo,
      revisarYContinuar,
      usarPdf,
    };
  },
});
