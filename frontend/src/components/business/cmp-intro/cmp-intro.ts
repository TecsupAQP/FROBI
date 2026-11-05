import { defineComponent } from "vue";
import { useRouter } from "vue-router";
import VButton from "@/components/base/v-button/v-button.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VChipPieza from "@/components/base/v-chip-pieza/v-chip-pieza.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import useCmpPerfil from "@/composables/common/cmp-perfil/cmp-perfil.composable";
import { PIEZAS } from "@/constants/piezas.constant";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpIntro",
  components: { VButton, VChip, VChipPieza, CmpEncabezadoPagina },
  setup() {
    const PREFIX = "cmp-intro";

    const IDEAS = [
      {
        titulo: "Puede ayudarte a entender",
        texto: "Explica un tema de otra forma, con ejemplos y paso a paso.",
      },
      {
        titulo: "Puede equivocarse",
        texto: "No siempre tiene razón. Compara con tu guía y con fuentes antes de confiar.",
      },
      { titulo: "Pídele bien las cosas", texto: "Una buena instrucción tiene 4 piezas:", piezas: true },
    ];

    const router = useRouter();

    const { perfil, marcarIntroVista } = useCmpPerfil();

    const seguir = async () => {
      await marcarIntroVista();
      router.push(
        perfil.value.vioAsistente
          ? { name: perfil.value.modo === "docente" ? RutaEnum.CLASE_NUEVA : RutaEnum.INICIO }
          : { name: RutaEnum.ASISTENTE, params: { paso: 1 } },
      );
    };

    return { PIEZAS, PREFIX, IDEAS, seguir };
  },
});
