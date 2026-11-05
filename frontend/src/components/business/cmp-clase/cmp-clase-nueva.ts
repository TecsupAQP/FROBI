import { computed, defineComponent, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import VButton from "@/components/base/v-button/v-button.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VField from "@/components/base/v-field/v-field.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import CmpSubirPdf from "@/components/business/cmp-inicio/modals/cmp-subir-pdf/cmp-subir-pdf.vue";
import useCmpClase from "@/composables/common/cmp-clase/cmp-clase.composable";
import useCmpInicio from "@/composables/business/cmp-inicio/cmp-inicio.composable";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpClaseNueva",
  components: { VButton, VChip, VField, VIcon, CmpEncabezadoPagina, CmpSubirPdf },
  setup() {
    const PREFIX = "cmp-clase-nueva";

    const REGLAS = [
      "Da pistas y pasos primero; la respuesta llega al final.",
      "Permite practicar sin IA y lo cuenta como logro.",
      "Adapta formatos según el perfil de accesibilidad de cada estudiante.",
    ];

    const router = useRouter();

    const { materiales, ocupado, cargarMateriales, crear } = useCmpClase();

    // La subida usa el mismo modal (simulado) de Inicio.
    const {
      archivo,
      fase,
      modalAbierto,
      nombreArchivo,
      progreso,
      tamanoArchivoMb,
      abrirModal,
      cancelarSubida,
      cerrarModal,
      elegirArchivo,
    } = useCmpInicio();

    const nombre = ref("Sensores industriales · Mecatrónica");

    const primeraTarea = ref("Elegir un sensor para detectar botellas");

    const errorNombre = ref<string>();

    // El título muestra solo el nombre, sin la carrera que va después del "·".
    const nombreCorto = computed(() => nombre.value.split("·")[0]?.trim() ?? "");

    const agregarMaterial = () => {
      if (archivo.value && !materiales.value.includes(archivo.value.nombre)) {
        materiales.value = [...materiales.value, archivo.value.nombre];
      }
      cerrarModal();
    };

    const crearYSeguir = async () => {
      if (nombre.value.trim().length < 3) {
        errorNombre.value = "Escribe un nombre para la clase.";
        document.getElementById("clase-nombre")?.focus();
        return;
      }
      errorNombre.value = undefined;
      await crear({ nombre: nombreCorto.value || nombre.value, carrera: "Mecatrónica", ciclo: "ciclo 1" });
      router.push({ name: RutaEnum.CLASE_INVITAR });
    };

    onMounted(cargarMateriales);

    return {
      PREFIX,
      REGLAS,
      materiales,
      ocupado,
      archivo,
      fase,
      modalAbierto,
      nombreArchivo,
      progreso,
      tamanoArchivoMb,
      abrirModal,
      cancelarSubida,
      elegirArchivo,
      nombre,
      primeraTarea,
      errorNombre,
      nombreCorto,
      agregarMaterial,
      crearYSeguir,
    };
  },
});
