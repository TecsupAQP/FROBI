import { ref } from "vue";
import { defineStore } from "pinia";
import type { Progreso } from "@/core/shared/domain/view/progreso.view";
import { EstadoCargaEnum } from "@/core/shared/application/enum/estado-carga.enum";
import { obtenerProgresoService } from "@/core/progreso/infraestructure/adapters/in/service/progreso.service";

export const useCmpProgresoStore = defineStore("CmpProgresoStore", () => {
  const progreso = ref<Progreso | null>(null);
  const estado = ref<EstadoCargaEnum>(EstadoCargaEnum.INICIAL);

  const cargar = async (alias: string) => {
    estado.value = EstadoCargaEnum.CARGANDO;
    progreso.value = await obtenerProgresoService(alias);
    estado.value = progreso.value ? EstadoCargaEnum.LISTO : EstadoCargaEnum.VACIO;
  };

  return { estado, progreso, cargar };
});
