import { onMounted, watch } from "vue";
import useCmpAjustes from "@/composables/common/cmp-ajustes/cmp-ajustes.composable";

// Lleva los interruptores de Ajustes a atributos de <html>; los estilos de cada modo viven en _tokens.scss.
function useAplicarAjustes() {
  const { ajustes, cargar } = useCmpAjustes();

  const aplicar = () => {
    const raiz = document.documentElement;
    const { activos, idioma } = ajustes.value;
    raiz.lang = idioma;
    raiz.toggleAttribute("data-contrast", activos.contraste);
    raiz.toggleAttribute("data-text-scale", activos.contraste);
    raiz.toggleAttribute("data-buttons-large", activos["botones-grandes"]);
    raiz.toggleAttribute("data-textos-cortos", activos["textos-cortos"]);
    raiz.toggleAttribute("data-subtitulos", activos.subtitulos);
  };

  watch(ajustes, aplicar, { deep: true });
  onMounted(async () => {
    await cargar();
    aplicar();
  });
}

export default useAplicarAjustes;
