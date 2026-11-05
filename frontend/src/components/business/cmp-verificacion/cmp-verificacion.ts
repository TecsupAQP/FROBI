import { computed, defineComponent, onMounted } from "vue";
import { useRouter } from "vue-router";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import CmpPregunta from "@/components/business/cmp-verificacion/content/cmp-pregunta/cmp-pregunta.vue";
import useCmpVerificacion from "@/composables/business/cmp-verificacion/cmp-verificacion.composable";
import { FORMATOS } from "@/constants/formatos.constant";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpVerificacion",
  components: { VAviso, VButton, VCargando, VIcon, CmpEncabezadoPagina, CmpPregunta },
  setup() {
    const PREFIX = "cmp-verificacion";

    const router = useRouter();

    const {
      acerto,
      elegida,
      esUltima,
      indice,
      pregunta,
      revisando,
      total,
      verificacion,
      cargar,
      reintentar,
      responder,
      siguiente,
    } = useCmpVerificacion();

    const formatoSugerido = computed(
      () => FORMATOS.find((formato) => formato.id === pregunta.value?.formatoSugerido) ?? FORMATOS[0]!,
    );

    const avanzar = () => {
      if (esUltima.value) {
        router.push({ name: RutaEnum.CIERRE });
        return;
      }
      siguiente();
    };

    onMounted(cargar);

    return {
      RutaEnum,
      PREFIX,
      router,
      acerto,
      elegida,
      esUltima,
      indice,
      pregunta,
      revisando,
      total,
      verificacion,
      reintentar,
      responder,
      siguiente,
      formatoSugerido,
      avanzar,
    };
  },
});
