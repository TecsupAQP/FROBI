import { defineComponent, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import VButton from "@/components/base/v-button/v-button.vue";
import VField from "@/components/base/v-field/v-field.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VLogo from "@/components/base/v-logo/v-logo.vue";
import VRadioOpcion from "@/components/base/v-radio-opcion/v-radio-opcion.vue";
import VSelect from "@/components/base/v-select/v-select.vue";
import CmpPanelMarca from "@/components/business/cmp-login/content/cmp-panel-marca/cmp-panel-marca.vue";
import useCmpLogin from "@/composables/business/cmp-login/cmp-login.composable";
import useCmpSesion from "@/composables/common/cmp-sesion/cmp-sesion.composable";
import useCmpPerfil from "@/composables/common/cmp-perfil/cmp-perfil.composable";
import type { Rol } from "@/core/shared/domain/view/student.view";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpLogin",
  components: { VButton, VField, VIcon, VLogo, VRadioOpcion, VSelect, CmpPanelMarca },
  setup() {
    const PREFIX = "cmp-login";

    const ROLES: { valor: Rol; nombre: string }[] = [
      { valor: "estudiante", nombre: "Estudiante" },
      { valor: "docente", nombre: "Docente" },
    ];

    const router = useRouter();

    const route = useRoute();

    const { alias, carrera, carreras, codigoClase, enviando, errores, rol, cargarCarreras, entrar } =
      useCmpLogin();

    const { iniciarSesion } = useCmpSesion();

    const { perfil, cargar: cargarPerfil, elegirModo, guardar } = useCmpPerfil();

    const enviar = async () => {
      const sesion = await entrar();
      if (!sesion) {
        // Lleva el foco al primer campo con error.
        document.querySelector<HTMLElement>(`.${PREFIX} [aria-invalid="true"]`)?.focus();
        return;
      }
      iniciarSesion(sesion);
      // Con un código válido la persona entra por la puerta de clase.
      if (sesion.clase) {
        await cargarPerfil();
        elegirModo("estudiante-clase");
        perfil.value.codigoClase = codigoClase.value.trim().toUpperCase();
        await guardar();
      }
      const volver = route.query.volver;
      // Vuelve a la pantalla que pidió entrar; desde el inicio se sigue el flujo normal (elegir rol).
      if (
        typeof volver === "string" &&
        volver.startsWith("/") &&
        volver !== "/" &&
        !volver.startsWith("/login")
      ) {
        router.push(volver);
      } else {
        router.push({ name: RutaEnum.ROL });
      }
    };

    onMounted(() => {
      cargarCarreras();
      // El enlace de invitación trae el código: /login?clase=ABC123
      if (typeof route.query.clase === "string") codigoClase.value = route.query.clase;
    });

    return { PREFIX, ROLES, alias, carrera, carreras, codigoClase, enviando, errores, rol, enviar };
  },
});
