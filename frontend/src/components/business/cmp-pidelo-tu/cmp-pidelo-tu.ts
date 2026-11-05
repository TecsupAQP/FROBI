import { computed, defineComponent, onMounted } from "vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import CmpAutonomia from "@/components/business/cmp-pidelo-tu/content/cmp-autonomia/cmp-autonomia.vue";
import CmpEditorInstruccion from "@/components/business/cmp-pidelo-tu/content/cmp-editor-instruccion/cmp-editor-instruccion.vue";
import CmpPlantilla from "@/components/business/cmp-pidelo-tu/content/cmp-plantilla/cmp-plantilla.vue";
import CmpPuntajePiezas from "@/components/business/cmp-pidelo-tu/content/cmp-puntaje-piezas/cmp-puntaje-piezas.vue";
import CmpSugerencia from "@/components/business/cmp-pidelo-tu/content/cmp-sugerencia/cmp-sugerencia.vue";
import CmpComparacion from "@/components/business/cmp-pidelo-tu/content/cmp-comparacion/cmp-comparacion.vue";
import VButton from "@/components/base/v-button/v-button.vue";
import CmpResultadoMejorada from "@/components/business/cmp-pidelo-tu/content/cmp-resultado-mejorada/cmp-resultado-mejorada.vue";
import useCmpPideloTu from "@/composables/business/cmp-pidelo-tu/cmp-pidelo-tu.composable";
import useCmpResultado from "@/composables/business/cmp-resultado/cmp-resultado.composable";
import useCmpAvisos from "@/composables/common/cmp-avisos/cmp-avisos.composable";
import { nombrePieza } from "@/constants/piezas.constant";
import { RutaEnum, TAREA_EJEMPLO } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpPideloTu",
  components: {
    CmpEncabezadoPagina,
    CmpAutonomia,
    CmpEditorInstruccion,
    CmpPlantilla,
    CmpPuntajePiezas,
    CmpSugerencia,
    CmpComparacion,
    VButton,
    CmpResultadoMejorada,
  },
  props: {
    tema: { type: String, default: "" },
  },
  setup(props) {
    const PREFIX = "cmp-pidelo-tu";

    // El tema es el de la última adaptación que vio la persona.
    const { adaptacion } = useCmpResultado();

    const temaActual = computed(() => props.tema || adaptacion.value?.titulo || "");

    const descripcion = computed(() =>
      temaActual.value
        ? `Escribe cómo quieres que la IA te explique el tema «${temaActual.value}».`
        : "Escribe cómo quieres que la IA te explique tu guía.",
    );

    const {
      autonomia,
      evaluacion,
      fase,
      instruccion,
      mejorada,
      piezasEscritas,
      plantilla,
      puedePedir,
      anadirEjemplo,
      iniciar,
      mejorarInstruccion,
      pedirALaIA,
      probarOtra,
      usarPlantilla,
    } = useCmpPideloTu();

    const { mostrarAviso } = useCmpAvisos();

    const copiarReceta = async () => {
      const texto = (mejorada.value?.receta ?? [])
        .map((pieza) => `${nombrePieza(pieza.pieza)}: ${pieza.texto}`)
        .join("\n");
      try {
        await navigator.clipboard.writeText(texto);
      } catch {
        // Portapapeles no disponible (http, permisos): el aviso se muestra igual.
      }
      mostrarAviso("Receta copiada", "Pégala donde quieras. Se oculta en 4 s.");
    };

    onMounted(iniciar);

    return {
      descripcion,
      RutaEnum,
      TAREA_EJEMPLO,
      PREFIX,
      autonomia,
      evaluacion,
      fase,
      instruccion,
      mejorada,
      piezasEscritas,
      plantilla,
      puedePedir,
      anadirEjemplo,
      mejorarInstruccion,
      pedirALaIA,
      probarOtra,
      usarPlantilla,
      copiarReceta,
    };
  },
});
