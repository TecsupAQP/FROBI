import { PdfIlegibleError, type MaterialPort } from "@/core/material/infraestructure/ports/in/material.port";
import type { ArchivoLeido, Material, Tema } from "@/core/shared/domain/view/material.view";
import { api, esErrorApi } from "@/core/shared/infraestructure/http/api.client";
import type { MaterialDto } from "@/core/shared/infraestructure/http/api.dto";
import { elegirMaterial, materialActualId } from "@/core/shared/infraestructure/http/contexto-estudio";
import { CARRERAS } from "@/constants/carreras.constant";
import { tituloDeGuia, tituloDesdeArchivo } from "@/core/shared/application/util/texto.util";

const PALABRAS_POR_MINUTO = 180;
const LARGO_VISTA_PREVIA = 420;

// El texto extraído usa "## Título" para cada sección: cada una es un tema de la guía.
export function temasDesdeTexto(texto: string): Tema[] {
  const bloques = texto
    .split(/^##\s+/m)
    .map((bloque) => bloque.trim())
    .filter(Boolean);
  const conTitulo = /^##\s+/m.test(texto);
  return bloques.map((bloque, indice) => {
    const [primera = "", ...resto] = bloque.split("\n");
    return {
      id: `tema-${indice + 1}`,
      numero: indice + 1,
      titulo: conTitulo ? primera.trim() : bloques.length === 1 ? "Todo el material" : `Parte ${indice + 1}`,
      textoOriginal: (conTitulo ? resto.join(" ") : bloque).replace(/\s+/g, " ").trim(),
    };
  });
}

export function materialDesdeApi(dto: MaterialDto, carrera: string): Material {
  const temas = temasDesdeTexto(dto.extracted_text);
  const palabras = dto.extracted_text.split(/\s+/).length;
  return {
    id: dto.id,
    titulo: tituloDeGuia(dto.title),
    carrera,
    descripcion: temas[0]?.textoOriginal.split(". ").slice(0, 2).join(". ") ?? "",
    etiquetas: temas
      .slice(1, 4)
      .map((tema) => tema.titulo.replace(/^Sensores\s+/i, ""))
      .map((titulo) => titulo.charAt(0).toUpperCase() + titulo.slice(1)),
    minutosLectura: Math.max(1, Math.round(palabras / PALABRAS_POR_MINUTO)),
    temas,
  };
}

const carreraDeLaSesion = (): string => {
  try {
    const sesion = JSON.parse(localStorage.getItem("frobi-sesion") ?? "null") as {
      estudiante?: { carrera?: string };
    } | null;
    const id = sesion?.estudiante?.carrera ?? "";
    return CARRERAS.find((carrera) => carrera.id === id && id !== "otra")?.nombre ?? "tu carrera";
  } catch {
    return "tu carrera";
  }
};

// GET /materials/{id}, POST /materials/upload (PDF) y POST /materials (texto pegado).
export class MaterialUseCase implements MaterialPort {
  async obtenerGuia(): Promise<Material> {
    const dto = await api.get<MaterialDto>(`/materials/${await materialActualId()}`);
    return materialDesdeApi(dto, carreraDeLaSesion());
  }

  async leerPdf(archivo: File, alAvanzar: (porcentaje: number) => void): Promise<ArchivoLeido> {
    // fetch no informa el avance de la subida: se marca al enviar y al terminar.
    alAvanzar(15);
    const formulario = new FormData();
    formulario.append("file", archivo);
    formulario.append("title", tituloDesdeArchivo(archivo.name));
    formulario.append("kind", "guide");
    const avance = window.setInterval(() => alAvanzar(60), 400);
    try {
      const dto = await api.enviarFormulario<MaterialDto>("/materials/upload", formulario);
      alAvanzar(100);
      const [primerTema] = temasDesdeTexto(dto.extracted_text);
      return {
        materialId: dto.id,
        nombre: archivo.name,
        tamanoMb: Math.round((archivo.size / 1024 / 1024) * 10) / 10,
        texto: dto.extracted_text.replace(/^##\s+/gm, "").trim(),
        vistaPrevia: {
          titulo: primerTema?.titulo ?? dto.title,
          texto: dto.extracted_text
            .replace(/^##\s+.*$/gm, "")
            .replace(/\s+/g, " ")
            .trim()
            .slice(0, LARGO_VISTA_PREVIA),
        },
      };
    } catch (error) {
      if (esErrorApi(error, "Materials.PdfUnreadable") || (esErrorApi(error) && error.status === 422)) {
        throw new PdfIlegibleError();
      }
      throw error;
    } finally {
      window.clearInterval(avance);
    }
  }

  async pegarTexto(titulo: string, texto: string): Promise<string> {
    const dto = await api.post<MaterialDto>("/materials", { title: titulo, kind: "guide", text: texto });
    return dto.id;
  }

  usarMaterial(materialId: string): void {
    elegirMaterial(materialId);
  }
}
