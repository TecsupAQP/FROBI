import { computed, defineComponent } from "vue";
import { useRoute } from "vue-router";
import VLogo from "@/components/base/v-logo/v-logo.vue";
import useCmpSesion from "@/composables/common/cmp-sesion/cmp-sesion.composable";
import { RutaEnum, SeccionNavEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpBarraSuperior",
  components: { VLogo },
  setup() {
    const PREFIX = "cmp-barra-superior";

    const route = useRoute();

    const { estudiante, esDocente, inicial } = useCmpSesion();

    const pestanas = computed(() => {
      const seccion = route.meta.seccion;
      const base = [
        { nombre: "Inicio", ruta: RutaEnum.INICIO, seccion: SeccionNavEnum.INICIO },
        { nombre: "Guía", ruta: RutaEnum.GUIA, seccion: SeccionNavEnum.GUIA },
        esDocente.value
          ? { nombre: "Panel docente", ruta: RutaEnum.DOCENTE, seccion: SeccionNavEnum.DOCENTE }
          : { nombre: "Mi progreso", ruta: RutaEnum.PROGRESO, seccion: SeccionNavEnum.PROGRESO },
      ];
      return base.map((pestana) => ({ ...pestana, activa: pestana.seccion === seccion }));
    });

    return { RutaEnum, PREFIX, estudiante, inicial, pestanas };
  },
});
