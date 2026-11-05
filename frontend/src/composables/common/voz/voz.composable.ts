import { computed, ref } from "vue";
import useCmpAjustes from "@/composables/common/cmp-ajustes/cmp-ajustes.composable";

const hablando = ref(false);

// Lectura en voz alta con la Web Speech API del navegador (no es IA: es la voz del sistema).
function useVoz() {
  const { ajustes } = useCmpAjustes();

  const disponible = typeof window !== "undefined" && "speechSynthesis" in window;
  const vozActiva = computed(() => ajustes.value.activos.voz);

  const leer = (texto: string) => {
    if (!disponible || !texto.trim()) return false;
    window.speechSynthesis.cancel();
    const frase = new SpeechSynthesisUtterance(texto);
    frase.lang = "es-PE";
    frase.onstart = () => (hablando.value = true);
    frase.onend = () => (hablando.value = false);
    frase.onerror = () => (hablando.value = false);
    window.speechSynthesis.speak(frase);
    return true;
  };

  const detener = () => {
    if (disponible) window.speechSynthesis.cancel();
    hablando.value = false;
  };

  return { disponible, hablando, vozActiva, detener, leer };
}

export default useVoz;
