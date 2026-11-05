import { defineComponent, nextTick, onBeforeUnmount, ref, useModel, watch } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";

export default defineComponent({
  name: "VModal",
  components: { VButton },
  props: {
    id: { type: String, required: true },
    titulo: { type: String, required: true },
    descripcion: { type: String, default: undefined },
    modelValue: { type: Boolean, default: false },
  },
  emits: {
    "update:modelValue": (_valor: boolean) => true,
  },
  setup(props, { expose }) {
    const abierto = useModel(props, "modelValue");

    const PREFIX = "v-modal";

    const ENFOCABLES =
      'a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])';

    const dialogo = ref<HTMLElement | null>(null);

    let focoPrevio: HTMLElement | null = null;

    const cerrar = () => {
      abierto.value = false;
    };

    // Mantiene el foco dentro del diálogo y cierra con Escape.
    const alPresionar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") {
        evento.stopPropagation();
        cerrar();
        return;
      }
      if (evento.key !== "Tab" || !dialogo.value) return;
      const enfocables = [...dialogo.value.querySelectorAll<HTMLElement>(ENFOCABLES)];
      const primero = enfocables[0];
      const ultimo = enfocables[enfocables.length - 1];
      if (!primero || !ultimo) return;
      if (evento.shiftKey && document.activeElement === primero) {
        evento.preventDefault();
        ultimo.focus();
      } else if (!evento.shiftKey && document.activeElement === ultimo) {
        evento.preventDefault();
        primero.focus();
      }
    };

    watch(
      abierto,
      async (valor) => {
        document.body.style.overflow = valor ? "hidden" : "";
        if (valor) {
          focoPrevio = document.activeElement as HTMLElement | null;
          await nextTick();
          dialogo.value?.focus();
        } else {
          focoPrevio?.focus();
        }
      },
      { immediate: true },
    );

    onBeforeUnmount(() => {
      document.body.style.overflow = "";
    });

    expose({ id: props.id });

    return { PREFIX, dialogo, cerrar, alPresionar, abierto };
  },
});
