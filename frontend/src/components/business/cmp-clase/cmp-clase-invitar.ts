import { computed, defineComponent, onMounted, ref } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VField from "@/components/base/v-field/v-field.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import CmpAlumnoItem from "@/components/business/cmp-clase/content/cmp-alumno-item/cmp-alumno-item.vue";
import useCmpAvisos from "@/composables/common/cmp-avisos/cmp-avisos.composable";
import useCmpClase from "@/composables/common/cmp-clase/cmp-clase.composable";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpClaseInvitar",
  components: { VButton, VCargando, VChip, VField, VIcon, CmpEncabezadoPagina, CmpAlumnoItem },
  setup() {
    const PREFIX = "cmp-clase-invitar";

    const { clase, ocupado, cargar, invitar } = useCmpClase();

    const { mostrarAviso } = useCmpAvisos();

    const correo = ref("");

    const errorCorreo = ref<string>();

    const enlace = computed(() => `${window.location.origin}/login?clase=${clase.value?.codigo ?? ""}`);

    const copiar = async (texto: string, titulo: string) => {
      try {
        await navigator.clipboard.writeText(texto);
      } catch {
        // Portapapeles no disponible: en la maqueta el aviso se muestra igual.
      }
      mostrarAviso(titulo, "Compártelo con tus alumnos.");
    };

    // Maqueta: no se envía ningún correo; el alumno aparece como invitación pendiente.
    const enviar = async () => {
      if (!/^\S+@\S+\.\S+$/.test(correo.value.trim())) {
        errorCorreo.value = "Escribe un correo válido.";
        document.getElementById("invitar-correo")?.focus();
        return;
      }
      errorCorreo.value = undefined;
      await invitar(correo.value.trim());
      mostrarAviso("Invitación enviada", `${correo.value.trim()} aparece como pendiente.`);
      correo.value = "";
    };

    onMounted(cargar);

    return { RutaEnum, PREFIX, clase, ocupado, invitar, correo, errorCorreo, enlace, copiar, enviar };
  },
});
