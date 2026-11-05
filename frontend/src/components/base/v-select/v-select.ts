import {
  computed,
  defineComponent,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  useModel,
  type PropType,
} from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";

export interface OpcionSelect {
  id: string;
  nombre: string;
}

export default defineComponent({
  name: "VSelect",
  components: { VIcon },
  props: {
    id: { type: String, required: true },
    etiqueta: { type: String, required: true },
    opciones: { type: Array as PropType<OpcionSelect[]>, required: true },
    placeholder: { type: String, default: "Elige una opción" },
    error: { type: String, default: undefined },
    modelValue: { type: String, default: "" },
  },
  emits: {
    "update:modelValue": (_valor: string) => true,
  },
  setup(props) {
    const modelo = useModel(props, "modelValue");

    const PREFIX = "v-select";

    const raiz = ref<HTMLElement | null>(null);

    const boton = ref<HTMLButtonElement | null>(null);

    const lista = ref<HTMLUListElement | null>(null);

    const abierto = ref(false);

    const activa = ref(-1);

    const seleccionada = computed(() => props.opciones.find((opcion) => opcion.id === modelo.value));

    const abrir = async () => {
      abierto.value = true;
      activa.value = Math.max(
        0,
        props.opciones.findIndex((opcion) => opcion.id === modelo.value),
      );
      await nextTick();
      lista.value?.focus();
    };

    const cerrar = (devolverFoco = true) => {
      abierto.value = false;
      if (devolverFoco) boton.value?.focus();
    };

    const alternar = () => (abierto.value ? cerrar() : abrir());

    const elegir = (indice: number) => {
      const opcion = props.opciones[indice];
      if (opcion) modelo.value = opcion.id;
      cerrar();
    };

    const alPresionarEnBoton = (evento: KeyboardEvent) => {
      if (["ArrowDown", "ArrowUp"].includes(evento.key)) {
        evento.preventDefault();
        abrir();
      }
    };

    const alPresionarEnLista = (evento: KeyboardEvent) => {
      const ultima = props.opciones.length - 1;
      const acciones: Record<string, () => void> = {
        ArrowDown: () => (activa.value = Math.min(ultima, activa.value + 1)),
        ArrowUp: () => (activa.value = Math.max(0, activa.value - 1)),
        Home: () => (activa.value = 0),
        End: () => (activa.value = ultima),
        Enter: () => elegir(activa.value),
        " ": () => elegir(activa.value),
        Escape: () => cerrar(),
        Tab: () => cerrar(false),
      };
      const accion = acciones[evento.key];
      if (!accion) return;
      if (evento.key !== "Tab") evento.preventDefault();
      accion();
      nextTick(() =>
        document.getElementById(`${props.id}-opcion-${activa.value}`)?.scrollIntoView({ block: "nearest" }),
      );
    };

    const alHacerClicFuera = (evento: MouseEvent) => {
      if (abierto.value && raiz.value && !raiz.value.contains(evento.target as Node)) cerrar(false);
    };

    onMounted(() => document.addEventListener("mousedown", alHacerClicFuera));

    onBeforeUnmount(() => document.removeEventListener("mousedown", alHacerClicFuera));

    return {
      PREFIX,
      raiz,
      boton,
      lista,
      abierto,
      activa,
      seleccionada,
      alternar,
      elegir,
      alPresionarEnBoton,
      alPresionarEnLista,
      modelo,
    };
  },
});
