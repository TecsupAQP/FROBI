import { computed, defineComponent, onMounted, ref } from "vue";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VBarraDato from "@/components/base/v-barra-dato/v-barra-dato.vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VEstadoVacio from "@/components/base/v-estado-vacio/v-estado-vacio.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import useCmpClase from "@/composables/common/cmp-clase/cmp-clase.composable";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpAlumno",
  components: { VAviso, VBarraDato, VButton, VCargando, VChip, VEstadoVacio, VIcon, CmpEncabezadoPagina },
  props: {
    alias: { type: String, required: true },
  },
  setup(props) {
    const PREFIX = "cmp-alumno";

    const MENSAJES_RESUMEN = 3;

    const { detalle, cargarDetalle } = useCmpClase();

    const cargando = ref(true);

    const completa = ref(false);

    // El resumen muestra los primeros mensajes; la API hoy no comparte conversaciones con el docente.
    const mensajesVisibles = computed(() =>
      completa.value
        ? (detalle.value?.conversacion ?? [])
        : (detalle.value?.conversacion ?? []).slice(0, MENSAJES_RESUMEN),
    );

    onMounted(async () => {
      try {
        await cargarDetalle(props.alias);
      } catch {
        // Sin permiso o sin conexión: se muestra el estado "No encontramos a este alumno".
      } finally {
        cargando.value = false;
      }
    });

    return { RutaEnum, PREFIX, detalle, cargando, completa, mensajesVisibles };
  },
});
