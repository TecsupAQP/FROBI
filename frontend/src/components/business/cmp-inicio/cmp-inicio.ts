import { defineComponent, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import CmpTarjetaGuia from "@/components/business/cmp-inicio/content/cmp-tarjeta-guia/cmp-tarjeta-guia.vue";
import CmpMisGuias from "@/components/business/cmp-inicio/content/cmp-mis-guias/cmp-mis-guias.vue";
import CmpTarjetaSubir from "@/components/business/cmp-inicio/content/cmp-tarjeta-subir/cmp-tarjeta-subir.vue";
import CmpSubirPdf from "@/components/business/cmp-inicio/modals/cmp-subir-pdf/cmp-subir-pdf.vue";
import useCmpInicio from "@/composables/business/cmp-inicio/cmp-inicio.composable";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpInicio",
  components: { VCargando, CmpTarjetaGuia, CmpTarjetaSubir, CmpSubirPdf, CmpMisGuias },
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
      guias,
      modalAbierto,
      nombreArchivo,
      progreso,
      tamanoArchivoMb,
      abrirModal,
      cancelarSubida,
      cargarGuia,
      cerrarModal,
      elegirArchivo,
      elegirGuia,
      usarGuia: usarMaterial,
    } = useCmpInicio();

    const eligiendo = ref<string | null>(null);

    // Cambia la guía que se estudia y la deja arriba, en la tarjeta principal.
    const estudiar = async (id: string) => {
      eligiendo.value = id;
      try {
        await elegirGuia(id);
        window.scrollTo({ top: 0, behavior: "smooth" });
      } finally {
        eligiendo.value = null;
      }
    };

    const usarGuia = async (textoPegado?: string) => {
      await usarMaterial(textoPegado);
      cerrarModal();
      router.push({ name: RutaEnum.GUIA });
    };

    onMounted(cargarGuia);

    return {
      PREFIX,
      archivo,
      fase,
      guia,
      guias,
      eligiendo,
      estudiar,
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
