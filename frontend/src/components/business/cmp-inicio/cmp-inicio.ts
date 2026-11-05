import { defineComponent, onMounted } from "vue";
import { useRouter } from "vue-router";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import CmpTarjetaGuia from "@/components/business/cmp-inicio/content/cmp-tarjeta-guia/cmp-tarjeta-guia.vue";
import CmpTarjetaSubir from "@/components/business/cmp-inicio/content/cmp-tarjeta-subir/cmp-tarjeta-subir.vue";
import CmpSubirPdf from "@/components/business/cmp-inicio/modals/cmp-subir-pdf/cmp-subir-pdf.vue";
import useCmpInicio from "@/composables/business/cmp-inicio/cmp-inicio.composable";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpInicio",
  components: { VCargando, CmpTarjetaGuia, CmpTarjetaSubir, CmpSubirPdf },
  props: {
    alias: { type: String, required: true },
  },
  setup() {
    const PREFIX = "cmp-inicio";

    const router = useRouter();

    const {
      archivo,
      fase,
      guia,
      modalAbierto,
      nombreArchivo,
      progreso,
      tamanoArchivoMb,
      abrirModal,
      cancelarSubida,
      cargarGuia,
      cerrarModal,
      elegirArchivo,
    } = useCmpInicio();

    const usarGuia = () => {
      cerrarModal();
      router.push({ name: RutaEnum.GUIA });
    };

    onMounted(cargarGuia);

    return {
      PREFIX,
      archivo,
      fase,
      guia,
      modalAbierto,
      nombreArchivo,
      progreso,
      tamanoArchivoMb,
      abrirModal,
      cancelarSubida,
      elegirArchivo,
      usarGuia,
    };
  },
});
