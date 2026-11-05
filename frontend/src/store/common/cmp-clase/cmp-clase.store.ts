import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type {
  AvanceGuiaClase,
  Clase,
  DetalleAlumno,
  MaterialClase,
  NuevaClase,
  PlanGuia,
} from "@/core/shared/domain/view/clase.view";
import {
  avanceGuiasClaseService,
  crearClaseService,
  guardarPlanGuiaService,
  invitarService,
  listarMaterialesClaseService,
  obtenerClaseService,
  obtenerDetalleAlumnoService,
  salirDeClaseService,
  subirMaterialClaseService,
} from "@/core/clase/infraestructure/adapters/in/service/clase.service";

// Puerta de clase: el docente solo ve la actividad que ocurre dentro de su clase.
export const useCmpClaseStore = defineStore("CmpClaseStore", () => {
  const clase = ref<Clase | null>(null);
  const cargada = ref(false);
  // PDFs elegidos antes de crear la clase: se suben cuando la clase existe.
  const pendientes = ref<File[]>([]);
  const detalle = ref<DetalleAlumno | null>(null);
  // Contenido ya subido a la clase (lo ven sus alumnos unidos).
  const contenido = ref<MaterialClase[]>([]);
  // Avance de cada alumno en cada guía (solo el docente).
  const avances = ref<AvanceGuiaClase[]>([]);
  const subiendo = ref(false);
  const guardando = ref<string | null>(null);
  const errorContenido = ref<string | null>(null);
  const ocupado = ref(false);

  const materiales = computed(() => pendientes.value.map((archivo) => archivo.name));
  const estoyEnClase = computed(() => clase.value !== null);

  const cargar = async (forzar = false) => {
    if (cargada.value && !forzar) return;
    clase.value = await obtenerClaseService();
    cargada.value = true;
  };

  const agregarMaterial = (archivo: File) => {
    if (!pendientes.value.some((item) => item.name === archivo.name)) {
      pendientes.value = [...pendientes.value, archivo];
    }
  };

  const crear = async (datos: Omit<NuevaClase, "archivos">) => {
    ocupado.value = true;
    try {
      clase.value = await crearClaseService({ ...datos, archivos: pendientes.value });
      cargada.value = true;
      pendientes.value = [];
    } finally {
      ocupado.value = false;
    }
  };

  const invitar = async (aliasOCorreo: string) => {
    ocupado.value = true;
    try {
      clase.value = await invitarService(aliasOCorreo);
    } finally {
      ocupado.value = false;
    }
  };

  const cargarDetalle = async (alias: string) => {
    detalle.value = null;
    detalle.value = await obtenerDetalleAlumnoService(alias);
  };

  const cargarContenido = async () => {
    errorContenido.value = null;
    try {
      [contenido.value, avances.value] = await Promise.all([
        listarMaterialesClaseService(),
        avanceGuiasClaseService().catch(() => []),
      ]);
    } catch {
      contenido.value = [];
      avances.value = [];
    }
  };

  const subirContenido = async (archivo: File, plan: PlanGuia) => {
    subiendo.value = true;
    errorContenido.value = null;
    try {
      contenido.value = await subirMaterialClaseService(archivo, plan);
      avances.value = await avanceGuiasClaseService().catch(() => avances.value);
    } catch (error) {
      // La API explica el motivo (sin texto, escaneo de más de 20 páginas, más de 10 MB…).
      errorContenido.value =
        error instanceof Error && error.message
          ? error.message
          : "No pudimos subir el archivo. Revisa que sea un PDF de hasta 10 MB.";
    } finally {
      subiendo.value = false;
    }
  };

  // Cambia el tipo de una guía o sus tareas; las tareas sin cambios conservan el avance.
  const guardarPlan = async (materialId: string, plan: PlanGuia) => {
    guardando.value = materialId;
    errorContenido.value = null;
    try {
      contenido.value = await guardarPlanGuiaService(materialId, plan);
      avances.value = await avanceGuiasClaseService().catch(() => avances.value);
    } catch {
      errorContenido.value = "No pudimos guardar la guía. Revisa que tenga entre 1 y 20 tareas.";
    } finally {
      guardando.value = null;
    }
  };

  const salir = async () => {
    await salirDeClaseService();
    clase.value = null;
  };

  const reiniciar = () => {
    clase.value = null;
    cargada.value = false;
    pendientes.value = [];
    detalle.value = null;
    contenido.value = [];
    avances.value = [];
  };

  return {
    avances,
    clase,
    contenido,
    detalle,
    errorContenido,
    guardando,
    subiendo,
    estoyEnClase,
    materiales,
    ocupado,

    agregarMaterial,
    cargar,
    cargarContenido,
    cargarDetalle,
    crear,
    guardarPlan,
    invitar,
    reiniciar,
    salir,
    subirContenido,
  };
});
