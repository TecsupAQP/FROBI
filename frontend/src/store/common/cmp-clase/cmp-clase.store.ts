import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { Clase, DetalleAlumno, NuevaClase } from "@/core/shared/domain/view/clase.view";
import {
  crearClaseService,
  invitarService,
  obtenerClaseService,
  obtenerDetalleAlumnoService,
  salirDeClaseService,
} from "@/core/clase/infraestructure/adapters/in/service/clase.service";

// Puerta de clase: el docente solo ve la actividad que ocurre dentro de su clase.
export const useCmpClaseStore = defineStore("CmpClaseStore", () => {
  const clase = ref<Clase | null>(null);
  const cargada = ref(false);
  // PDFs elegidos antes de crear la clase: se suben cuando la clase existe.
  const pendientes = ref<File[]>([]);
  const detalle = ref<DetalleAlumno | null>(null);
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

  const salir = async () => {
    await salirDeClaseService();
    clase.value = null;
  };

  const reiniciar = () => {
    clase.value = null;
    cargada.value = false;
    pendientes.value = [];
    detalle.value = null;
  };

  return {
    clase,
    detalle,
    estoyEnClase,
    materiales,
    ocupado,

    agregarMaterial,
    cargar,
    cargarDetalle,
    crear,
    invitar,
    reiniciar,
    salir,
  };
});
