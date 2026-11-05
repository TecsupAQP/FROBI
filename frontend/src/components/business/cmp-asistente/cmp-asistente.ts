import { computed, defineComponent, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import VButton from "@/components/base/v-button/v-button.vue";
import VBotonEscuchar from "@/components/base/v-boton-escuchar/v-boton-escuchar.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VOpcionTarjeta from "@/components/base/v-opcion-tarjeta/v-opcion-tarjeta.vue";
import VPasos from "@/components/base/v-pasos/v-pasos.vue";
import CmpLayoutAsistente from "@/components/common/cmp-layout-asistente/cmp-layout-asistente.vue";
import useCmpAjustes from "@/composables/common/cmp-ajustes/cmp-ajustes.composable";
import useCmpPerfil from "@/composables/common/cmp-perfil/cmp-perfil.composable";
import { AJUSTES_ACCESIBILIDAD } from "@/constants/accesibilidad.constant";
import type { AjusteId } from "@/core/shared/domain/view/ajustes.view";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpAsistente",
  components: { VButton, VBotonEscuchar, VChip, VIcon, VOpcionTarjeta, VPasos, CmpLayoutAsistente },
  props: {
    paso: { type: Number, required: true },
  },
  setup(props) {
    const PREFIX = "cmp-asistente";

    const PREGUNTAS: Record<number, { titulo: string; subtitulo: string }> = {
      1: {
        titulo: "¿Quién va a usar FROBI?",
        subtitulo: "Son 3 pasos cortos. Puedes omitirlos y cambiarlos después.",
      },
      2: {
        titulo: "¿Qué te ayuda más a aprender?",
        subtitulo: "Marca todo lo que quieras. Si no estás seguro, elige la última opción.",
      },
      3: {
        titulo: "Listo. Así se verá FROBI para ti",
        subtitulo: "Puedes cambiarlo cuando quieras en Ajustes.",
      },
    };

    const PISTAS_VISTA = [
      "Busca en tu guía la parte que habla del tema.",
      "Compara las dos ideas principales: ¿en qué se diferencian?",
      "Escribe tu intento antes de ver la respuesta.",
      "Compara tu respuesta con tu guía.",
    ];

    const router = useRouter();

    const { perfil, guardando, cargar, elegirConfiguradoPor, marcarAsistenteVisto } = useCmpPerfil();

    const { ajustes, activarVarios, alternar, cargar: cargarAjustes } = useCmpAjustes();

    const noLoSe = ref(false);

    const pistaVista = ref(0);

    const lecturaPregunta = computed(
      () => `${PREGUNTAS[props.paso]?.titulo}. ${PREGUNTAS[props.paso]?.subtitulo}`,
    );

    const activados = computed(() =>
      AJUSTES_ACCESIBILIDAD.filter((ajuste) => ajustes.value.activos[ajuste.id]),
    );

    // Las ayudas son ajustes reales: se aplican al marcarlas y se ven en Ajustes.
    const elegirAyuda = (id: AjusteId) => {
      noLoSe.value = false;
      alternar(id);
    };

    // "No lo sé": se prueba con textos cortos y voz, que se pueden quitar en el paso 3.
    const alElegirNoLoSe = () => {
      if (noLoSe.value) activarVarios(["voz", "textos-cortos"], true);
    };

    const ir = (paso: number) => router.push({ name: RutaEnum.ASISTENTE, params: { paso } });

    const terminar = async () => {
      await marcarAsistenteVisto();
      router.push({ name: perfil.value.modo === "docente" ? RutaEnum.CLASE_NUEVA : RutaEnum.INICIO });
    };

    onMounted(() => {
      cargar();
      cargarAjustes();
    });

    return {
      AJUSTES_ACCESIBILIDAD,
      PREFIX,
      PREGUNTAS,
      PISTAS_VISTA,
      perfil,
      guardando,
      elegirConfiguradoPor,
      ajustes,
      noLoSe,
      pistaVista,
      lecturaPregunta,
      activados,
      elegirAyuda,
      alElegirNoLoSe,
      ir,
      terminar,
    };
  },
});
