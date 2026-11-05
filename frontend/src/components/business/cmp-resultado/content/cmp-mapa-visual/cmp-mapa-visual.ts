import { defineComponent, onBeforeUnmount, onMounted, ref, watch, type PropType } from "vue";
import type { Markmap } from "markmap-view";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { ContenidoMapaVisual } from "@/core/shared/domain/view/adaptation.view";

type NodoMapa = NonNullable<Parameters<typeof Markmap.create>[2]>;
type NodoPintado = Parameters<Markmap["options"]["color"]>[0];

// Una variable de color por rama; se leen de los tokens para respetar el alto contraste.
const COLORES_RAMA = [
  "--marca-azul",
  "--estado-exito",
  "--pieza-contexto-borde",
  "--pieza-formato-borde",
  "--pieza-nivel-borde",
  "--estado-error",
];

const escapar = (texto: string) =>
  texto.replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!,
  );

const nodo = (contenido: string, hijos: NodoMapa[] = []): NodoMapa => ({
  content: contenido,
  children: hijos,
});

// "Inductivo → solo metales" se dibuja como idea con su explicación colgando.
const punto = (texto: string): NodoMapa => {
  const [idea, ...resto] = texto.split(/\s*→\s*/);
  const explicacion = resto.join(" → ");
  return explicacion
    ? nodo(`<strong>${escapar(idea ?? "")}</strong>`, [nodo(escapar(explicacion))])
    : nodo(escapar(texto));
};

export function arbolDelMapa(contenido: ContenidoMapaVisual): NodoMapa {
  return nodo(
    `<strong>${escapar(contenido.conceptoCentral)}</strong>`,
    contenido.nodos.map((rama) =>
      nodo(`<strong>${escapar(rama.titulo)}</strong>`, [
        ...(rama.detalle ? [nodo(escapar(rama.detalle))] : []),
        ...rama.puntos.map(punto),
      ]),
    ),
  );
}

// Mapa mental interactivo (Markmap): las ramas se pliegan, se puede acercar y mover.
// Debajo va la misma información como lista, para lectores de pantalla y para quien prefiera leer.
export default defineComponent({
  name: "CmpMapaVisual",
  components: { VAviso, VIcon },
  props: {
    contenido: { type: Object as PropType<ContenidoMapaVisual>, required: true },
  },
  setup(props) {
    const PREFIX = "cmp-mapa-visual";

    const lienzo = ref<SVGSVGElement | null>(null);

    const listo = ref(false);

    const fallo = ref(false);

    let mapa: Markmap | null = null;

    const colorDe = (nodoPintado: NodoPintado) => {
      const rama = Number(nodoPintado.state.path.split(".")[1] ?? 0);
      const variable = COLORES_RAMA[rama % COLORES_RAMA.length] ?? COLORES_RAMA[0]!;
      return getComputedStyle(document.documentElement).getPropertyValue(variable).trim() || "#1d4ed8";
    };

    const dibujar = async () => {
      if (!lienzo.value) return;
      try {
        // Se carga solo cuando se abre el mapa visual (no pesa en el resto de la app).
        const { Markmap } = await import("markmap-view");
        const sinMovimiento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        const opciones = {
          // No se reencuadra solo al abrir ramas: así el texto no se achica por debajo de 16 px.
          autoFit: false,
          // Nunca se agranda por encima del tamaño real al encuadrar.
          maxInitialScale: 1,
          duration: sinMovimiento ? 0 : 400,
          color: colorDe,
          maxWidth: 280,
          spacingVertical: 10,
          spacingHorizontal: 90,
          paddingX: 12,
          // Se arranca con el tema y sus ramas; cada rama se abre al tocarla (de a poco se aprende mejor).
          initialExpandLevel: 2,
        };
        const datos = arbolDelMapa(props.contenido);
        if (mapa) {
          await mapa.setData(datos, opciones);
        } else {
          mapa = Markmap.create(lienzo.value, opciones, datos);
          seguirRamaAbierta(mapa, opciones.duration);
        }
        await encuadrarLegible();
        listo.value = true;
      } catch {
        fallo.value = true;
      }
    };

    // Al abrir una rama, el mapa se desplaza lo justo para que se vean sus ideas (sin achicar el texto).
    const seguirRamaAbierta = (instancia: Markmap, duracion: number) => {
      const original = instancia.handleClick;
      instancia.handleClick = (evento, nodoTocado) => {
        original(evento, nodoTocado);
        window.setTimeout(async () => {
          const hijos = nodoTocado.children ?? [];
          if (nodoTocado.payload?.fold || !hijos.length) return;
          const margen = { left: 24, right: 24, top: 16, bottom: 16 };
          await instancia.ensureVisible(hijos[hijos.length - 1]!, margen);
          await instancia.ensureVisible(hijos[0]!, margen);
        }, duracion + 50);
      };
    };

    // Encuadra sin agrandar por encima del tamaño real (el texto queda en 16 px).
    const encuadrarLegible = async () => {
      await mapa?.fit(1);
    };

    const acercar = () => mapa?.rescale(1.25);
    const alejar = () => mapa?.rescale(0.8);
    const ajustar = () => mapa?.fit();

    let pausa = 0;
    const alCambiarTamano = () => {
      window.clearTimeout(pausa);
      pausa = window.setTimeout(() => encuadrarLegible(), 200);
    };

    watch(() => props.contenido, dibujar, { deep: true });

    onMounted(() => {
      dibujar();
      window.addEventListener("resize", alCambiarTamano);
    });

    onBeforeUnmount(() => {
      window.removeEventListener("resize", alCambiarTamano);
      window.clearTimeout(pausa);
      mapa?.destroy();
      mapa = null;
    });

    return { PREFIX, lienzo, listo, fallo, acercar, alejar, ajustar };
  },
});
