import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { Adaptation, FormatoId } from "@/core/shared/domain/view/adaptation.view";
import { EstadoCargaEnum } from "@/core/shared/application/enum/estado-carga.enum";
import { SinConexionError } from "@/core/shared/application/util/errores.util";
import { obtenerAdaptacionService } from "@/core/adaptacion/infraestructure/adapters/in/service/adaptacion.service";

export const useCmpResultadoStore = defineStore("CmpResultadoStore", () => {
  const adaptacion = ref<Adaptation | null>(null);
  const estado = ref<EstadoCargaEnum>(EstadoCargaEnum.INICIAL);
  const formatoActual = ref<FormatoId>("mapa-visual");
  const recetaDesplegada = ref(true);

  const estaCargando = computed(() => estado.value === EstadoCargaEnum.CARGANDO);
  const usaRespaldo = computed(() => adaptacion.value?.esRespaldo === true);

  // Evita que una respuesta lenta de un formato anterior pise a la más reciente.
  let ultimaSolicitud = 0;

  const cargarAdaptacion = async (temaId: string, formato: FormatoId, forzar = false) => {
    // V2 ya la dejó lista antes de navegar: no se vuelve a pedir (salvo "Reintentar con la IA").
    const actual = adaptacion.value;
    if (
      !forzar &&
      actual?.temaId === temaId &&
      actual.contenido.formato === formato &&
      estado.value !== EstadoCargaEnum.CARGANDO
    ) {
      formatoActual.value = formato;
      return;
    }
    const solicitud = ++ultimaSolicitud;
    formatoActual.value = formato;
    estado.value = EstadoCargaEnum.CARGANDO;
    try {
      const respuesta = await obtenerAdaptacionService(temaId, formato);
      if (solicitud !== ultimaSolicitud) return;
      adaptacion.value = respuesta;
      estado.value = respuesta.esRespaldo ? EstadoCargaEnum.ERROR_RESPALDO : EstadoCargaEnum.LISTO;
    } catch (error) {
      if (solicitud !== ultimaSolicitud) return;
      adaptacion.value = null;
      estado.value =
        error instanceof SinConexionError ? EstadoCargaEnum.SIN_CONEXION : EstadoCargaEnum.ERROR_RESPALDO;
    }
  };

  const alternarReceta = () => {
    recetaDesplegada.value = !recetaDesplegada.value;
  };

  return {
    adaptacion,
    estado,
    estaCargando,
    formatoActual,
    recetaDesplegada,
    usaRespaldo,

    alternarReceta,
    cargarAdaptacion,
  };
});
