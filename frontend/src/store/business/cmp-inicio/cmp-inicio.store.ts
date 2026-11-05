import { ref } from "vue";
import { defineStore } from "pinia";
import type { ArchivoLeido, FaseSubida, Material } from "@/core/shared/domain/view/material.view";
import { PdfIlegibleError } from "@/core/material/infraestructure/ports/in/material.port";
import {
  leerPdfService,
  obtenerGuiaService,
} from "@/core/material/infraestructure/adapters/in/service/material.service";

export const useCmpInicioStore = defineStore("CmpInicioStore", () => {
  const guia = ref<Material | null>(null);
  const modalAbierto = ref(false);
  const fase = ref<FaseSubida>("elegir");
  const progreso = ref(0);
  const archivo = ref<ArchivoLeido | null>(null);
  const nombreArchivo = ref("");
  const tamanoArchivoMb = ref(0);

  let subidaActual = 0;

  const cargarGuia = async () => {
    guia.value = await obtenerGuiaService("guia-sensores");
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

  // Maqueta: no se sube ningún archivo real, se simula la lectura de guia-sensores.pdf.
  const elegirArchivo = async (nombre = "guia-sensores.pdf", tamanoMb = 2.4) => {
    const subida = ++subidaActual;
    nombreArchivo.value = nombre;
    tamanoArchivoMb.value = tamanoMb;
    progreso.value = 0;
    fase.value = "subiendo";
    try {
      const leido = await leerPdfService(nombre, (porcentaje) => {
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

  const cancelarSubida = () => {
    subidaActual++;
    fase.value = archivo.value ? "listo" : "elegir";
  };

  return {
    archivo,
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
  };
});
