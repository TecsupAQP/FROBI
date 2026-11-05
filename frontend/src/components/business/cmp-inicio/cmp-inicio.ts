import { computed, defineComponent, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VEstadoVacio from "@/components/base/v-estado-vacio/v-estado-vacio.vue";
import CmpTarjetaGuia from "@/components/business/cmp-inicio/content/cmp-tarjeta-guia/cmp-tarjeta-guia.vue";
import CmpMisGuias from "@/components/business/cmp-inicio/content/cmp-mis-guias/cmp-mis-guias.vue";
import CmpTarjetaSubir from "@/components/business/cmp-inicio/content/cmp-tarjeta-subir/cmp-tarjeta-subir.vue";
import CmpSubirPdf from "@/components/business/cmp-inicio/modals/cmp-subir-pdf/cmp-subir-pdf.vue";
import useCmpInicio from "@/composables/business/cmp-inicio/cmp-inicio.composable";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpInicio",
  components: {
    VAviso,
    VButton,
    VEstadoVacio,
    VCargando,
    CmpTarjetaGuia,
    CmpTarjetaSubir,
    CmpSubirPdf,
    CmpMisGuias,
  },
  props: {
    alias: { type: String, required: true },
  },
  setup() {
    const PREFIX = "cmp-inicio";

    const router = useRouter();

    const route = useRoute();

    // Se llegó aquí desde una pantalla de estudio sin tener guía.
    const vieneSinGuia = computed(() => route.query.sinGuia === "1");

    const {
      archivo,
      fase,
      guia,
      guiaEjemplo,
      guiasClase,
      nombreClase,
      propias,
      sinGuia,
      modalAbierto,
      motivoError,
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

    // Abre una guía de la clase (si no es la actual) y lleva a su tarea o a su evaluación final.
    const irConGuia = async (guiaId: string, destino: Parameters<typeof router.push>[0]) => {
      eligiendo.value = guiaId;
      try {
        if (!guiasClase.value.find((item) => item.id === guiaId)?.actual) await elegirGuia(guiaId);
        await router.push(destino);
      } finally {
        eligiendo.value = null;
      }
    };

    const resolverTarea = (guiaId: string, tareaRef: string) =>
      irConGuia(guiaId, { name: RutaEnum.AYUDA, params: { tarea: tareaRef } });

    const evaluarGuia = (guiaId: string) => irConGuia(guiaId, { name: RutaEnum.VERIFICACION });

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
      guiaEjemplo,
      guiasClase,
      nombreClase,
      propias,
      sinGuia,
      vieneSinGuia,
      eligiendo,
      estudiar,
      resolverTarea,
      evaluarGuia,
      modalAbierto,
      motivoError,
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
