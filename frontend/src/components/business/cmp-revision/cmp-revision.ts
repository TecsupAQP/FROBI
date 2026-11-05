import { defineComponent, onMounted } from "vue";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VSemaforo from "@/components/base/v-semaforo/v-semaforo.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import CmpSeccionRevisada from "@/components/business/cmp-revision/content/cmp-seccion-revisada/cmp-seccion-revisada.vue";
import useCmpTrabajo from "@/composables/business/cmp-trabajo/cmp-trabajo.composable";
import { SEMAFORO } from "@/constants/semaforo.constant";
import type { EstadoAfirmacion } from "@/core/shared/domain/view/claim-review.view";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpRevision",
  components: { VAviso, VButton, VCargando, VSemaforo, CmpEncabezadoPagina, CmpSeccionRevisada },
  setup() {
    const PREFIX = "cmp-revision";

    const ESTADOS: EstadoAfirmacion[] = ["con-respaldo", "no-comprobable", "contradice"];

    const { revision, asegurarRevision } = useCmpTrabajo();

    onMounted(asegurarRevision);

    return { SEMAFORO, RutaEnum, PREFIX, ESTADOS, revision };
  },
});
