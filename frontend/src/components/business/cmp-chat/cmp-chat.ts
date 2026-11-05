import { computed, defineComponent, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import CmpEscribiendo from "@/components/business/cmp-chat/content/cmp-escribiendo/cmp-escribiendo.vue";
import CmpMensajeChat from "@/components/business/cmp-chat/content/cmp-mensaje-chat/cmp-mensaje-chat.vue";
import logoIcono from "@/assets/resources/images/logo-frobi-icono.svg";
import useCmpChat from "@/composables/business/cmp-chat/cmp-chat.composable";
import useCmpSesion from "@/composables/common/cmp-sesion/cmp-sesion.composable";
import { SUGERENCIAS_DOCENTE, SUGERENCIAS_ESTUDIANTE } from "@/constants/asistente.constant";

const MAX_CARACTERES = 2000;
const ALTO_MAXIMO_CAMPO = 168;
// Si la persona subió a leer algo anterior, no se la baja de golpe al llegar texto nuevo.
const CERCA_DEL_FINAL = 120;

export default defineComponent({
  name: "CmpChat",
  components: { VAviso, VIcon, CmpEscribiendo, CmpMensajeChat },
  setup() {
    const PREFIX = "cmp-chat";

    const {
      borrador,
      conexion,
      consultando,
      error,
      habilitado,
      lineas,
      preguntasRestantes,
      respondiendo,
      abrir,
      cerrar,
      enviar,
      nuevaConversacion,
    } = useCmpChat();
    const { estudiante, esDocente } = useCmpSesion();

    const texto = ref("");
    const campo = ref<HTMLTextAreaElement | null>(null);
    const desplazable = ref<HTMLElement | null>(null);

    const alias = computed(() => estudiante.value?.alias ?? "");
    const sugerencias = computed(() => (esDocente.value ? SUGERENCIAS_DOCENTE : SUGERENCIAS_ESTUDIANTE));
    const presentacion = computed(() =>
      esDocente.value
        ? "Te ayudo a seguir a tu clase: quién necesita apoyo, qué alertas hay y cómo usar FROBI con tus alumnos."
        : "Te ayudo a entender tu guía, a ver cómo vas y a usar FROBI. Pregúntame lo que quieras.",
    );
    const placeholder = computed(() => (esDocente.value ? "Pregunta por tu clase…" : "Escribe tu pregunta…"));

    const estadoVisible = computed(() => {
      if (conexion.value === "conectando") return { clave: "conectando", texto: "Conectando…" };
      if (conexion.value === "sin-conexion")
        return { clave: "sin-conexion", texto: "Sin conexión · reintentando" };
      if (respondiendo.value) return { clave: "en-linea", texto: "Escribiendo…" };
      return { clave: "en-linea", texto: habilitado.value ? "En línea" : "En línea · ayuda básica" };
    });

    // Los puntos se ven hasta que empieza a llegar la respuesta.
    const esperandoTexto = computed(
      () => respondiendo.value && !lineas.value.some((linea) => linea.estado === "escribiendo"),
    );

    const puedeEnviar = computed(
      () => texto.value.trim().length > 0 && !respondiendo.value && conexion.value === "en-linea",
    );

    const ajustarAltura = () => {
      const elemento = campo.value;
      if (!elemento) return;
      elemento.style.height = "auto";
      elemento.style.height = `${Math.min(elemento.scrollHeight, ALTO_MAXIMO_CAMPO)}px`;
    };

    const bajar = async (forzar = false) => {
      await nextTick();
      const caja = desplazable.value;
      if (!caja) return;
      const cerca = caja.scrollHeight - caja.scrollTop - caja.clientHeight < CERCA_DEL_FINAL;
      if (forzar || cerca) caja.scrollTo({ top: caja.scrollHeight });
    };

    const preguntar = (pregunta: string) => {
      if (enviar(pregunta)) void bajar(true);
    };

    const enviarBorrador = () => {
      if (!puedeEnviar.value) return;
      if (enviar(texto.value)) {
        texto.value = "";
        void nextTick(ajustarAltura);
        void bajar(true);
      }
    };

    // Una pregunta rechazada vuelve al campo para corregirla.
    watch(borrador, (valor) => {
      if (valor) {
        texto.value = valor;
        void nextTick(ajustarAltura);
      }
    });

    watch(
      () => lineas.value.map((linea) => linea.texto.length).join(),
      () => void bajar(),
    );
    watch(esperandoTexto, () => void bajar());

    onMounted(async () => {
      await abrir();
      // Sin mensajes se ve la bienvenida desde arriba; con historial, lo último.
      if (lineas.value.length) void bajar(true);
      campo.value?.focus();
    });
    onBeforeUnmount(cerrar);

    return {
      MAX_CARACTERES,
      PREFIX,
      alias,
      campo,
      conexion,
      consultando,
      desplazable,
      error,
      esperandoTexto,
      estadoVisible,
      habilitado,
      lineas,
      logoIcono,
      placeholder,
      preguntasRestantes,
      presentacion,
      puedeEnviar,
      respondiendo,
      sugerencias,
      texto,
      ajustarAltura,
      enviarBorrador,
      nuevaConversacion,
      preguntar,
    };
  },
});
