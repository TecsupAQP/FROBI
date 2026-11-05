import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { Clase, DetalleAlumno, MaterialClase, NuevaClase } from "@/core/shared/domain/view/clase.view";
import {
  crearClaseService,
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
  const subiendo = ref(false);
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
      contenido.value = await listarMaterialesClaseService();
    } catch {
      contenido.value = [];
    }
  };

  const subirContenido = async (archivo: File) => {
    subiendo.value = true;
    errorContenido.value = null;
    try {
      contenido.value = await subirMaterialClaseService(archivo);
    } catch {
      errorContenido.value = "No pudimos subir el archivo. Revisa que sea un PDF con texto, de hasta 10 MB.";
    } finally {
      subiendo.value = false;
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
  };

  return {
    clase,
    contenido,
    detalle,
    errorContenido,
    subiendo,
    estoyEnClase,
    materiales,
    ocupado,

    agregarMaterial,
    cargar,
    cargarContenido,
    cargarDetalle,
    crear,
    invitar,
    reiniciar,
    salir,
    subirContenido,
  };
});
