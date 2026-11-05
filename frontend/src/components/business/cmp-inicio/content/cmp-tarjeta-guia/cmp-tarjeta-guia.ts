import { defineComponent, type PropType } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { Material } from "@/core/shared/domain/view/material.view";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpTarjetaGuia",
  components: { VButton, VIcon },
  props: {
    guia: { type: Object as PropType<Material>, required: true },
  },
  setup() {
    const PREFIX = "cmp-tarjeta-guia";

    return { RutaEnum, PREFIX };
  },
});
