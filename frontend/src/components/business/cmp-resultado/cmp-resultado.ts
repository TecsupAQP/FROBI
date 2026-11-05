import { computed, defineComponent, watch, type PropType } from "vue";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import CmpSelectorFormato from "@/components/business/cmp-resultado/content/cmp-selector-formato/cmp-selector-formato.vue";
import CmpTarjetaResultado from "@/components/business/cmp-resultado/content/cmp-tarjeta-resultado/cmp-tarjeta-resultado.vue";
import CmpMapaVisual from "@/components/business/cmp-resultado/content/cmp-mapa-visual/cmp-mapa-visual.vue";
import CmpEjemploReal from "@/components/business/cmp-resultado/content/cmp-ejemplo-real/cmp-ejemplo-real.vue";
import CmpLecturaFacil from "@/components/business/cmp-resultado/content/cmp-lectura-facil/cmp-lectura-facil.vue";
import CmpAudio from "@/components/business/cmp-resultado/content/cmp-audio/cmp-audio.vue";
import CmpRecetaIa from "@/components/business/cmp-resultado/content/cmp-receta-ia/cmp-receta-ia.vue";
import useCmpResultado from "@/composables/business/cmp-resultado/cmp-resultado.composable";
import useCmpAvisos from "@/composables/common/cmp-avisos/cmp-avisos.composable";
import { FORMATOS } from "@/constants/formatos.constant";
import { nombrePieza } from "@/constants/piezas.constant";
import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";
import { EstadoCargaEnum } from "@/core/shared/application/enum/estado-carga.enum";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpResultado",
  components: {
    VAviso,
    VButton,
    VCargando,
    VIcon,
    CmpSelectorFormato,
    CmpTarjetaResultado,
    CmpMapaVisual,
    CmpEjemploReal,
    CmpLecturaFacil,
    CmpAudio,
    CmpRecetaIa,
  },
  props: {
    temaId: { type: String, required: true },
    formato: { type: String as PropType<FormatoId>, required: true },
  },
  emits: {
    reintentar: () => true,
  },
  setup(props) {
    const PREFIX = "cmp-resultado";

    const {
      adaptacion,
      estado,
      estaCargando,
      formatoActual,
      recetaDesplegada,
      alternarReceta,
      cargarAdaptacion,
    } = useCmpResultado();

    const { mostrarAviso } = useCmpAvisos();

    // El store conserva la adaptación anterior mientras carga otro formato, así la pantalla no salta.
    const ruta = computed(() => adaptacion.value?.ruta ?? []);

    const titulo = computed(() => adaptacion.value?.titulo ?? "Resultado");

    const receta = computed(() => adaptacion.value?.receta ?? []);

    const contenido = computed(() => adaptacion.value?.contenido);

    const definicionFormato = computed(
      () => FORMATOS.find((formato) => formato.id === formatoActual.value) ?? FORMATOS[0]!,
    );

    const copiarReceta = async () => {
      // Se copia la misma instrucción que FROBI le envió a la IA.
      const texto =
        adaptacion.value?.instruccion ||
        receta.value.map((pieza) => `${nombrePieza(pieza.pieza)}: ${pieza.texto}`).join("\n");
      try {
        await navigator.clipboard.writeText(texto);
      } catch {
        // El portapapeles puede no estar disponible (http, permisos); el aviso se muestra igual.
      }
      mostrarAviso("Receta copiada", "Pégala donde quieras. Se oculta en 4 s.");
    };

    watch(
      () => [props.temaId, props.formato] as const,
      ([temaId, formato]) => cargarAdaptacion(temaId, formato),
      { immediate: true },
    );

    return {
      EstadoCargaEnum,
      RutaEnum,
      PREFIX,
      adaptacion,
      estado,
      estaCargando,
      formatoActual,
      recetaDesplegada,
      alternarReceta,
      cargarAdaptacion,
      ruta,
      titulo,
      receta,
      contenido,
      definicionFormato,
      copiarReceta,
    };
  },
});
