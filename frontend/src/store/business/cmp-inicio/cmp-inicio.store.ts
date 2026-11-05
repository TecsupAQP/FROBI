import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type {
  ArchivoLeido,
  FaseSubida,
  GuiaResumen,
  Material,
} from "@/core/shared/domain/view/material.view";
import { tituloDesdeArchivo } from "@/core/shared/application/util/texto.util";
import { SinGuiaError } from "@/core/shared/application/util/errores.util";
import { useCmpEscaleraStore } from "@/store/business/cmp-escalera/cmp-escalera.store";
import { useCmpSesionStore } from "@/store/common/cmp-sesion/cmp-sesion.store";
import {
  listarMaterialesClaseService,
  miAvanceGuiasService,
} from "@/core/clase/infraestructure/adapters/in/service/clase.service";
import type { AvanceGuia, MaterialClase } from "@/core/shared/domain/view/clase.view";
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

  // true cuando la persona aún no subió ni eligió una guía (la de ejemplo no se elige sola).
  const sinGuia = ref(false);

  // Tus guías; la de ejemplo solo aparece si la estás estudiando.
  const propias = computed(() => guias.value.filter((item) => item.origen !== "ejemplo" || item.actual));
  const guiaEjemplo = computed(() => guias.value.find((item) => item.origen === "ejemplo") ?? null);

  // Lo que el docente subió a la clase del estudiante (vacío si no está en una clase).
  const materialesClase = ref<MaterialClase[]>([]);
  const avancesClase = ref<AvanceGuia[]>([]);
  const nombreClase = computed(() => useCmpSesionStore().clase?.nombre ?? "");
  const guiasClase = computed<GuiaResumen[]>(() =>
    materialesClase.value.map((material) => {
      const avance = avancesClase.value.find((item) => item.materialId === material.id);
      return {
        id: material.id,
        titulo: material.titulo,
        origen: "clase",
        vistaPrevia: material.vistaPrevia,
        actual: material.id === guia.value?.id,
        enClase: {
          modo: material.modo,
          avance: avance?.avance ?? 0,
          tareas: material.tareas.map((tarea) => ({
            ref: tarea.ref,
            numero: tarea.numero,
            enunciado: tarea.enunciado,
            hecha: avance?.tareasHechas.includes(tarea.id) ?? false,
          })),
          evaluacion: avance?.evaluacion ?? null,
        },
      };
    }),
  );

  const cargarMaterialesClase = async () => {
    const sesion = useCmpSesionStore();
    if (sesion.estudiante?.rol !== "estudiante") {
      materialesClase.value = [];
      avancesClase.value = [];
      return;
    }
    [materialesClase.value, avancesClase.value] = await Promise.all([
      listarMaterialesClaseService().catch(() => []),
      miAvanceGuiasService().catch(() => []),
    ]);
  };

  const cargarGuia = async () => {
    [guias.value] = await Promise.all([listarGuiasService(), cargarMaterialesClase()]);
    try {
      guia.value = await obtenerGuiaService();
      sinGuia.value = false;
    } catch (error) {
      if (!(error instanceof SinGuiaError)) throw error;
      guia.value = null;
      sinGuia.value = true;
    }
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
    guiasClase,
    nombreClase,
    guiaEjemplo,
    propias,
    sinGuia,
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
