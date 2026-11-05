import { computed, defineComponent } from "vue";
import { useRoute } from "vue-router";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import useCmpSesion from "@/composables/common/cmp-sesion/cmp-sesion.composable";
import { RutaEnum } from "@/enums/ruta.enum";

// Acceso al asistente desde cualquier pantalla con sesión (menos desde el propio chat).
export default defineComponent({
  name: "CmpBotonAsistente",
  components: { VIcon },
  props: {
    // Sube por encima de la barra fija inferior (móvil y tablet).
    elevado: { type: Boolean, default: false },
  },
  setup() {
    const PREFIX = "cmp-boton-asistente";

    const ruta = useRoute();
    const { haIniciado } = useCmpSesion();

    const visible = computed(() => haIniciado.value && ruta.name !== RutaEnum.CHAT);

    return { PREFIX, RutaEnum, visible };
  },
});
