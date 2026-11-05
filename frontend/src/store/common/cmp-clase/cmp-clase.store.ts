import { ref } from "vue";
import { defineStore } from "pinia";
import type { Clase, DetalleAlumno, NuevaClase } from "@/core/shared/domain/view/clase.view";
import {
  crearClaseService,
  invitarPorCorreoService,
  obtenerClaseService,
  obtenerDetalleAlumnoService,
  obtenerMaterialesClaseService,
  salirDeClaseService,
} from "@/core/clase/infraestructure/adapters/in/service/clase.service";

// Puerta de clase: el docente solo ve la actividad que ocurre dentro de su clase.
export const useCmpClaseStore = defineStore("CmpClaseStore", () => {
  const clase = ref<Clase | null>(null);
  const materiales = ref<string[]>([]);
  const detalle = ref<DetalleAlumno | null>(null);
  const ocupado = ref(false);
  const estoyEnClase = ref(true);

  const cargar = async () => {
    if (!clase.value) clase.value = await obtenerClaseService();
  };

  const cargarMateriales = async () => {
    materiales.value = await obtenerMaterialesClaseService();
  };

  const crear = async (datos: NuevaClase) => {
    ocupado.value = true;
    try {
      clase.value = await crearClaseService(datos);
    } finally {
      ocupado.value = false;
    }
  };

  const invitar = async (correo: string) => {
    ocupado.value = true;
    try {
      clase.value = await invitarPorCorreoService(correo);
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
    estoyEnClase.value = false;
  };

  return {
    clase,
    detalle,
    estoyEnClase,
    materiales,
    ocupado,

    cargar,
    cargarDetalle,
    cargarMateriales,
    crear,
    invitar,
    salir,
  };
});
