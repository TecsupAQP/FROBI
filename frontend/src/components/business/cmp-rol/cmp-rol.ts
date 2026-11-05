import { defineComponent, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import VButton from "@/components/base/v-button/v-button.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VField from "@/components/base/v-field/v-field.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VOpcionTarjeta from "@/components/base/v-opcion-tarjeta/v-opcion-tarjeta.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import useCmpPerfil from "@/composables/common/cmp-perfil/cmp-perfil.composable";
import useCmpSesion from "@/composables/common/cmp-sesion/cmp-sesion.composable";
import type { ModoUso } from "@/core/shared/domain/view/perfil.view";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpRol",
  components: { VButton, VChip, VField, VIcon, VOpcionTarjeta, CmpEncabezadoPagina },
  setup() {
    const PREFIX = "cmp-rol";

    const NOMBRE_MODO: Record<ModoUso, string> = {
      docente: "Docente",
      "estudiante-clase": "Estudiante",
      autonomo: "Por tu cuenta",
    };

    const TEXTO_CONTINUAR: Record<ModoUso, string> = {
      docente: "Continuar como docente",
      "estudiante-clase": "Unirme a la clase",
      autonomo: "Continuar",
    };

    const router = useRouter();

    const { perfil, cargar, elegirModo, guardar, validarCodigo } = useCmpPerfil();

    const { estudiante, iniciarSesion } = useCmpSesion();

    const codigo = ref("");

    const errorCodigo = ref<string>();

    const claseEncontrada = ref<string>();

    const ocupado = ref(false);

    const continuar = async () => {
      if (!perfil.value.modo) return;
      ocupado.value = true;
      try {
        if (perfil.value.modo === "estudiante-clase") {
          const resultado = await validarCodigo(codigo.value);
          if (!resultado.valido) {
            errorCodigo.value = resultado.mensaje;
            document.getElementById("rol-codigo")?.focus();
            return;
          }
          errorCodigo.value = undefined;
          claseEncontrada.value = resultado.nombreClase;
        }
        await guardar();
        if (estudiante.value) {
          iniciarSesion({
            ...estudiante.value,
            rol: perfil.value.modo === "docente" ? "docente" : "estudiante",
          });
        }
        router.push({
          name: perfil.value.vioIntro ? RutaEnum.ASISTENTE : RutaEnum.INTRO,
          params: { paso: 1 },
        });
      } finally {
        ocupado.value = false;
      }
    };

    onMounted(async () => {
      await cargar();
      codigo.value = perfil.value.codigoClase ?? "";
    });

    return {
      PREFIX,
      NOMBRE_MODO,
      TEXTO_CONTINUAR,
      perfil,
      elegirModo,
      estudiante,
      codigo,
      errorCodigo,
      claseEncontrada,
      ocupado,
      continuar,
    };
  },
});
