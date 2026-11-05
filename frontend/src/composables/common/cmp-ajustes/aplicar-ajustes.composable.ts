import { watch } from "vue";
import useCmpAjustes from "@/composables/common/cmp-ajustes/cmp-ajustes.composable";
import useCmpSesion from "@/composables/common/cmp-sesion/cmp-sesion.composable";

// Lleva los interruptores de Ajustes a atributos de <html>; los estilos de cada modo viven en _tokens.scss.
function useAplicarAjustes() {
  const { ajustes, cargar } = useCmpAjustes();
  const { estudiante } = useCmpSesion();

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

  // Los ajustes son de la persona: se leen de la API apenas hay sesión (y al cambiar de persona).
  watch(
    estudiante,
    async (persona) => {
      if (!persona) return aplicar();
      try {
        await cargar();
      } catch {
        // Sin conexión: se mantienen los valores por defecto hasta la próxima carga.
      }
      aplicar();
    },
    { immediate: true },
  );
}

export default useAplicarAjustes;
