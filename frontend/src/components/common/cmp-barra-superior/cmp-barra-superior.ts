import { computed, defineComponent, ref } from "vue";
import { useRoute } from "vue-router";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VLogo from "@/components/base/v-logo/v-logo.vue";
import CmpMenuLateral from "@/components/common/cmp-menu-lateral/cmp-menu-lateral.vue";
import useCmpSesion from "@/composables/common/cmp-sesion/cmp-sesion.composable";
import { RutaEnum, SeccionNavEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpBarraSuperior",
  components: { CmpMenuLateral, VIcon, VLogo },
  setup() {
    const PREFIX = "cmp-barra-superior";

    const route = useRoute();

    const menuAbierto = ref(false);

    const { estudiante, esDocente, inicial } = useCmpSesion();

    const pestanas = computed(() => {
      const seccion = route.meta.seccion;
      const base = [
        { nombre: "Inicio", ruta: RutaEnum.INICIO, seccion: SeccionNavEnum.INICIO },
        { nombre: "Guía", ruta: RutaEnum.GUIA, seccion: SeccionNavEnum.GUIA },
        esDocente.value
          ? {
              nombre: "Panel docente",
              // En móvil no entra junto al menú: se acorta.
              nombreCorto: "Panel",
              ruta: RutaEnum.DOCENTE,
              seccion: SeccionNavEnum.DOCENTE,
            }
          : { nombre: "Mi progreso", ruta: RutaEnum.PROGRESO, seccion: SeccionNavEnum.PROGRESO },
      ];
      return base.map((pestana) => ({
        nombreCorto: pestana.nombre,
        ...pestana,
        activa: pestana.seccion === seccion,
      }));
    });

    return { RutaEnum, PREFIX, estudiante, inicial, pestanas, menuAbierto };
  },
});
