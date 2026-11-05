import { defineComponent, useModel, type PropType } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VField from "@/components/base/v-field/v-field.vue";
import VRadioOpcion from "@/components/base/v-radio-opcion/v-radio-opcion.vue";
import type { ModoGuia } from "@/core/shared/domain/view/clase.view";

// La API acepta hasta 20 tareas por guía.
const MAX_TAREAS = 20;

export default defineComponent({
  name: "CmpPlanGuia",
  components: { VButton, VField, VRadioOpcion },
  props: {
    // Para ids únicos cuando hay varios editores en la página.
    prefijoId: { type: String, required: true },
    modo: { type: String as PropType<ModoGuia>, default: "estudio" },
    tareas: { type: Array as PropType<string[]>, default: () => [] },
  },
  emits: {
    "update:modo": (_modo: ModoGuia) => true,
    "update:tareas": (_tareas: string[]) => true,
  },
  setup(props) {
    const PREFIX = "cmp-plan-guia";

    const modoElegido = useModel(props, "modo");
    const lista = useModel(props, "tareas");

    const elegirModo = (valor: string) => {
      const modo: ModoGuia = valor === "tareas" ? "tareas" : "estudio";
      modoElegido.value = modo;
      // Una guía con tareas empieza con un casillero listo para escribir. (El modelo lo controla
      // el padre: modoElegido no cambia hasta el siguiente render, por eso se usa `modo`.)
      if (modo === "tareas" && !lista.value.length) lista.value = [""];
    };

    const escribir = (indice: number, texto: string) => {
      lista.value = lista.value.map((tarea, i) => (i === indice ? texto : tarea));
    };

    const agregar = () => {
      if (lista.value.length < MAX_TAREAS) lista.value = [...lista.value, ""];
    };

    const quitar = (indice: number) => {
      lista.value = lista.value.filter((_tarea, i) => i !== indice);
    };

    return { PREFIX, MAX_TAREAS, modoElegido, lista, elegirModo, escribir, agregar, quitar };
  },
});
