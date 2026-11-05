// Convierte los SVG descargados de Figma (src/assets/resources/icons) en un registro
// tipado para <v-icon>. Conserva la geometría exacta y cambia el color fijo por currentColor.
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";

const origen = "src/assets/resources/icons";
const destino = "src/constants/iconos.constant.ts";

const iconos = readdirSync(origen)
  .filter((archivo) => archivo.endsWith(".svg"))
  .sort()
  .map((archivo) => {
    const svg = readFileSync(join(origen, archivo), "utf8");
    const viewBox = /viewBox="([^"]+)"/.exec(svg)?.[1] ?? "0 0 24 24";
    const figuras = [...svg.matchAll(/<(path|circle|rect|line|polyline|polygon)\b[^>]*\/>/g)]
      .map(([etiqueta]) => etiqueta)
      .filter((etiqueta) => !/<rect[^>]*fill="white"\/>/.test(etiqueta) || !svg.includes("clipPath"))
      .map((etiqueta) =>
        etiqueta
          .replace(/\s+id="[^"]*"/g, "")
          .replace(/stroke="(?!none)[^"]*"/g, 'stroke="currentColor"')
          .replace(/fill="(?!none)[^"]*"/g, 'fill="currentColor"'),
      );
    return { nombre: basename(archivo, ".svg"), viewBox, contenido: figuras.join("") };
  });

const cuerpo = iconos
  .map(
    ({ nombre, viewBox, contenido }) =>
      `  "${nombre}": {\n    viewBox: "${viewBox}",\n    contenido: '${contenido}',\n  },`,
  )
  .join("\n");

writeFileSync(
  destino,
  `// Archivo generado por scripts/generar-iconos.mjs. No editar a mano.\n` +
    `export interface DefinicionIcono {\n  viewBox: string;\n  contenido: string;\n}\n\n` +
    `export const ICONOS = {\n${cuerpo}\n} as const satisfies Record<string, DefinicionIcono>;\n\n` +
    `export type NombreIcono = keyof typeof ICONOS;\n`,
);
console.log(`${iconos.length} iconos generados en ${destino}`);
