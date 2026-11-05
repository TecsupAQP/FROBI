import { computed, defineComponent, ref, type PropType } from "vue";
import VBarraDato from "@/components/base/v-barra-dato/v-barra-dato.vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import CmpPlanGuia from "@/components/business/cmp-docente/content/cmp-plan-guia/cmp-plan-guia.vue";
import type {
  AvanceGuiaClase,
  MaterialClase,
  ModoGuia,
  PlanGuia,
} from "@/core/shared/domain/view/clase.view";

const FECHA = new Intl.DateTimeFormat("es-PE", { day: "numeric", month: "long" });

const planValido = (modo: ModoGuia, tareas: string[]) =>
  modo === "estudio" || tareas.some((tarea) => tarea.trim());

export default defineComponent({
  name: "CmpContenidoClase",
  components: { VBarraDato, VButton, VChip, VIcon, CmpPlanGuia },
  props: {
    materiales: { type: Array as PropType<MaterialClase[]>, required: true },
    // Avance de cada alumno en cada guía.
    avances: { type: Array as PropType<AvanceGuiaClase[]>, default: () => [] },
    subiendo: { type: Boolean, default: false },
    // Id de la guía cuyo tipo o tareas se están guardando.
    guardando: { type: String as PropType<string | null>, default: null },
    error: { type: String as PropType<string | null>, default: null },
  },
  emits: {
    subir: (_archivo: File, _plan: PlanGuia) => true,
    guardarPlan: (_materialId: string, _plan: PlanGuia) => true,
  },
  setup(props, { emit }) {
    const PREFIX = "cmp-contenido-clase";

    // Nueva guía: archivo, tipo y tareas antes de subirla.
    const creando = ref(false);
    const archivo = ref<File | null>(null);
    const modo = ref<ModoGuia>("estudio");
    const tareas = ref<string[]>([]);
    const selector = ref<HTMLInputElement | null>(null);

    const puedeSubir = computed(
      () => archivo.value !== null && planValido(modo.value, tareas.value) && !props.subiendo,
    );

    const abrirNueva = () => {
      creando.value = true;
      archivo.value = null;
      modo.value = "estudio";
      tareas.value = [];
    };

    const abrirSelector = () => selector.value?.click();

    const alElegir = (evento: Event) => {
      const entrada = evento.target as HTMLInputElement;
      archivo.value = entrada.files?.[0] ?? null;
      entrada.value = "";
    };

    const subir = () => {
      if (!archivo.value || !puedeSubir.value) return;
      emit("subir", archivo.value, { modo: modo.value, tareas: tareas.value });
      creando.value = false;
    };

    // Editar una guía ya subida.
    const editando = ref<string | null>(null);
    const modoEdicion = ref<ModoGuia>("estudio");
    const tareasEdicion = ref<string[]>([]);

    const editar = (material: MaterialClase) => {
      editando.value = material.id;
      modoEdicion.value = material.modo;
      tareasEdicion.value = material.tareas.map((tarea) => tarea.enunciado);
    };

    const guardar = (materialId: string) => {
      if (!planValido(modoEdicion.value, tareasEdicion.value)) return;
      emit("guardarPlan", materialId, { modo: modoEdicion.value, tareas: tareasEdicion.value });
      editando.value = null;
    };

    const avanceDe = (materialId: string) =>
      props.avances.find((avance) => avance.materialId === materialId)?.alumnos ?? [];

    const formatearFecha = (fecha: string) => FECHA.format(new Date(fecha));

    return {
      PREFIX,
      creando,
      archivo,
      modo,
      tareas,
      selector,
      puedeSubir,
      abrirNueva,
      abrirSelector,
      alElegir,
      subir,
      editando,
      modoEdicion,
      tareasEdicion,
      editar,
      guardar,
      planValido,
      avanceDe,
      formatearFecha,
    };
  },
});
