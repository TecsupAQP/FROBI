import { computed, defineComponent, onMounted } from "vue";
import { useRouter } from "vue-router";
import VButton from "@/components/base/v-button/v-button.vue";
import VCasilla from "@/components/base/v-casilla/v-casilla.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import useCmpAjustes from "@/composables/common/cmp-ajustes/cmp-ajustes.composable";
import useCmpPerfil from "@/composables/common/cmp-perfil/cmp-perfil.composable";
import { PERFILES_ACCESIBILIDAD } from "@/constants/accesibilidad.constant";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpPerfilAccesibilidad",
  components: { VButton, VCasilla, VChip, VIcon, CmpEncabezadoPagina },
  setup() {
    const PREFIX = "cmp-perfil-accesibilidad";

    const router = useRouter();

    const { perfil, guardando, alternarPerfil, cargar, guardar } = useCmpPerfil();

    const { activarVarios } = useCmpAjustes();

    const elegidos = computed(() =>
      PERFILES_ACCESIBILIDAD.filter((opcion) => perfil.value.perfiles.includes(opcion.id)),
    );

    const cambios = computed(() =>
      elegidos.value.length
        ? [...new Set(elegidos.value.flatMap((opcion) => opcion.cambios)), "Sin límite de tiempo"]
        : [],
    );

    const seguir = () => router.push({ name: RutaEnum.INICIO });

    // Guarda el perfil y enciende los ajustes que le corresponden (se pueden cambiar en Ajustes).
    const guardarYSeguir = async () => {
      await guardar();
      activarVarios(elegidos.value.flatMap((opcion) => opcion.ajustes));
      seguir();
    };

    onMounted(cargar);

    return {
      PERFILES_ACCESIBILIDAD,
      PREFIX,
      perfil,
      guardando,
      alternarPerfil,
      cambios,
      seguir,
      guardarYSeguir,
    };
  },
});
