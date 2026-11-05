import { PdfIlegibleError, type MaterialPort } from "@/core/material/infraestructure/ports/in/material.port";
import type { ArchivoLeido, GuiaResumen, Material } from "@/core/shared/domain/view/material.view";
import { api, esErrorApi } from "@/core/shared/infraestructure/http/api.client";
import type { MaterialDto, MaterialResumenDto } from "@/core/shared/infraestructure/http/api.dto";
import { elegirMaterial, materialActualId } from "@/core/shared/infraestructure/http/contexto-estudio";
import { CARRERAS } from "@/constants/carreras.constant";
import { temasDesdeTexto, tituloDeGuia, tituloDesdeArchivo } from "@/core/shared/application/util/texto.util";

const PALABRAS_POR_MINUTO = 180;
const LARGO_VISTA_PREVIA = 420;

export function materialDesdeApi(dto: MaterialDto, carrera: string): Material {
  const temas = temasDesdeTexto(dto.extracted_text);
  const palabras = dto.extracted_text.split(/\s+/).length;
  return {
    id: dto.id,
    titulo: tituloDeGuia(dto.title),
    carrera,
    descripcion: temas[0]?.textoOriginal.split(". ").slice(0, 2).join(". ") ?? "",
    etiquetas: temas.slice(1, 4).map((tema) => tema.titulo.charAt(0).toUpperCase() + tema.titulo.slice(1)),
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

  // GET /materials/guides: las propias (más recientes primero) y las de ejemplo.
  async listarGuias(): Promise<GuiaResumen[]> {
    const [guias, actual] = await Promise.all([
      api.get<MaterialResumenDto[]>("/materials/guides"),
      // Sin guía elegida todavía, ninguna se marca como actual.
      materialActualId().catch(() => null),
    ]);
    const ORIGEN: Record<MaterialResumenDto["source"], GuiaResumen["origen"]> = {
      sample: "ejemplo",
      upload: "pdf",
      paste: "texto",
    };
    return guias.map((guia) => ({
      id: guia.id,
      titulo: tituloDeGuia(guia.title),
      origen: ORIGEN[guia.source],
      vistaPrevia: guia.preview.replace(/##\s*/g, "").trim(),
      actual: guia.id === actual,
    }));
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
