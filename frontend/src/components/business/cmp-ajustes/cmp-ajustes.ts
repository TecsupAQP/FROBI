import { defineComponent, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VField from "@/components/base/v-field/v-field.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VSwitch from "@/components/base/v-switch/v-switch.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import useCmpAjustes from "@/composables/common/cmp-ajustes/cmp-ajustes.composable";
import useCmpAvisos from "@/composables/common/cmp-avisos/cmp-avisos.composable";
import useCmpRecorrido from "@/composables/common/cmp-recorrido/cmp-recorrido.composable";
import useCmpClase from "@/composables/common/cmp-clase/cmp-clase.composable";
import useCmpPerfil from "@/composables/common/cmp-perfil/cmp-perfil.composable";
import useCmpSesion from "@/composables/common/cmp-sesion/cmp-sesion.composable";
import useVoz from "@/composables/common/voz/voz.composable";
import { AJUSTES_ACCESIBILIDAD } from "@/constants/accesibilidad.constant";
import type { AjusteId } from "@/core/shared/domain/view/ajustes.view";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpAjustes",
  components: { VAviso, VButton, VChip, VField, VIcon, VSwitch, CmpEncabezadoPagina },
  setup() {
    const PREFIX = "cmp-ajustes";

    const router = useRouter();

    const { ajustes, idiomas, alternar, cargar } = useCmpAjustes();

    const { clase, estoyEnClase, cargar: cargarClase, salir } = useCmpClase();

    const { reiniciarAsistente } = useCmpPerfil();

    const { estudiante, cambiarAlias, actualizarClase, cerrarSesion } = useCmpSesion();

    const { mostrarAviso } = useCmpAvisos();

    const { disponible, leer } = useVoz();

    const alias = ref(estudiante.value?.alias ?? "");

    watch(estudiante, (valor) => (alias.value = valor?.alias ?? ""));

    const cambiar = (id: AjusteId) => {
      alternar(id);
      if (id === "voz" && ajustes.value.activos.voz) leer("La voz leerá cada paso.");
    };

    const guardarAlias = async () => {
      const limpio = alias.value.trim();
      if (!estudiante.value || limpio.length < 3 || limpio === estudiante.value.alias) return;
      try {
        await cambiarAlias(limpio);
        mostrarAviso("Alias guardado", `Ahora eres ${limpio}.`);
      } catch {
        alias.value = estudiante.value.alias;
        mostrarAviso("No pudimos cambiar tu alias", "Inténtalo de nuevo en un momento.");
      }
    };

    // Cierra la sesión en la API y vuelve a "Entrar".
    const salirDeFrobi = async () => {
      try {
        await cerrarSesion();
      } finally {
        router.push({ name: RutaEnum.LOGIN });
      }
    };

    const salirDeClase = async () => {
      await salir();
      actualizarClase(null);
      mostrarAviso("Saliste de la clase", "Tu docente ya no verá tu actividad.");
    };

    const { iniciar: verRecorrido } = useCmpRecorrido();

    const rehacerAsistente = async () => {
      await reiniciarAsistente();
      router.push({ name: RutaEnum.ASISTENTE, params: { paso: 1 } });
    };

    onMounted(() => {
      cargar();
      cargarClase();
    });

    return {
      AJUSTES_ACCESIBILIDAD,
      RutaEnum,
      PREFIX,
      router,
      ajustes,
      idiomas,
      clase,
      estoyEnClase,
      disponible,
      alias,
      cambiar,
      guardarAlias,
      salirDeClase,
      salirDeFrobi,
      rehacerAsistente,
      verRecorrido,
    };
  },
});
