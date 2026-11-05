import { ref } from "vue";
import { defineStore } from "pinia";
import type {
  ArchivoLeido,
  FaseSubida,
  GuiaResumen,
  Material,
} from "@/core/shared/domain/view/material.view";
import { tituloDesdeArchivo } from "@/core/shared/application/util/texto.util";
import { useCmpEscaleraStore } from "@/store/business/cmp-escalera/cmp-escalera.store";
import { useCmpResultadoStore } from "@/store/business/cmp-resultado/cmp-resultado.store";
import { PdfIlegibleError } from "@/core/material/infraestructure/ports/in/material.port";
import {
  leerPdfService,
  listarGuiasService,
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

  // Mis guías: las que subió o pegó la persona y las de ejemplo.
  const guias = ref<GuiaResumen[]>([]);

  const cargarGuia = async () => {
    const [actual, todas] = await Promise.all([obtenerGuiaService(), listarGuiasService()]);
    guia.value = actual;
    guias.value = todas;
  };

  // Cambia la guía que se estudia: la guía, las adaptaciones y la escalera pasan a usarla.
  const cambiarMaterial = (id: string) => {
    usarMaterialService(id);
    useCmpResultadoStore().olvidarAdaptacion();
    useCmpEscaleraStore().reiniciar();
    guia.value = null;
  };

  const elegirGuia = async (id: string) => {
    cambiarMaterial(id);
    await cargarGuia();
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
      cambiarMaterial(await pegarTextoService(titulo, textoPegado.trim()));
    } else if (archivo.value) {
      cambiarMaterial(archivo.value.materialId);
    }
  };

  const cancelarSubida = () => {
    subidaActual++;
    fase.value = archivo.value ? "listo" : "elegir";
  };

  return {
    guias,
    elegirGuia,
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
