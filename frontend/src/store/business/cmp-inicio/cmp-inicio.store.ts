import { ref } from "vue";
import { defineStore } from "pinia";
import type { ArchivoLeido, FaseSubida, Material } from "@/core/shared/domain/view/material.view";
import { tituloDesdeArchivo } from "@/core/shared/application/util/texto.util";
import { PdfIlegibleError } from "@/core/material/infraestructure/ports/in/material.port";
import {
  leerPdfService,
  obtenerGuiaService,
  pegarTextoService,
  usarMaterialService,
} from "@/core/material/infraestructure/adapters/in/service/material.service";

export const useCmpInicioStore = defineStore("CmpInicioStore", () => {
  const guia = ref<Material | null>(null);
  const modalAbierto = ref(false);
  const fase = ref<FaseSubida>("elegir");
  const progreso = ref(0);
  const archivo = ref<ArchivoLeido | null>(null);
  // El archivo tal como lo eligió la persona (el docente lo vuelve a subir a su clase).
  const archivoElegido = ref<File | null>(null);
  const nombreArchivo = ref("");
  const tamanoArchivoMb = ref(0);

  let subidaActual = 0;

  const cargarGuia = async () => {
    guia.value = await obtenerGuiaService();
  };

  const abrirModal = () => {
    fase.value = "elegir";
    progreso.value = 0;
    archivo.value = null;
    modalAbierto.value = true;
  };

  const cerrarModal = () => {
    subidaActual++;
    modalAbierto.value = false;
  };

  // Sube el PDF a la API y muestra el texto extraído para revisarlo.
  const elegirArchivo = async (elegido: File) => {
    const subida = ++subidaActual;
    archivoElegido.value = elegido;
    nombreArchivo.value = elegido.name;
    tamanoArchivoMb.value = Math.round((elegido.size / 1024 / 1024) * 10) / 10;
    progreso.value = 0;
    fase.value = "subiendo";
    try {
      const leido = await leerPdfService(elegido, (porcentaje) => {
        if (subida === subidaActual) progreso.value = porcentaje;
      });
      if (subida !== subidaActual) return;
      archivo.value = leido;
      fase.value = "listo";
    } catch (error) {
      if (subida !== subidaActual) return;
      fase.value = error instanceof PdfIlegibleError ? "error" : "elegir";
    }
  };

  // "Usar esta guía" (PDF leído) o "Usar este texto" (pegado cuando el PDF no se pudo leer).
  const usarGuia = async (textoPegado?: string) => {
    if (textoPegado?.trim()) {
      const titulo = tituloDesdeArchivo(nombreArchivo.value) || "Mi guía";
      usarMaterialService(await pegarTextoService(titulo, textoPegado.trim()));
    } else if (archivo.value) {
      usarMaterialService(archivo.value.materialId);
    }
    guia.value = null;
  };

  const cancelarSubida = () => {
    subidaActual++;
    fase.value = archivo.value ? "listo" : "elegir";
  };

  return {
    archivo,
    archivoElegido,
    fase,
    guia,
    modalAbierto,
    nombreArchivo,
    progreso,
    tamanoArchivoMb,

    abrirModal,
    cancelarSubida,
    cargarGuia,
    cerrarModal,
    elegirArchivo,
    usarGuia,
  };
});
