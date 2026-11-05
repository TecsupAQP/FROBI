import { defineComponent, ref, useModel, watch, type PropType } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VField from "@/components/base/v-field/v-field.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VModal from "@/components/base/v-modal/v-modal.vue";
import VProgressBar from "@/components/base/v-progress-bar/v-progress-bar.vue";
import type { ArchivoLeido } from "@/core/shared/domain/view/material.view";
import type { FaseSubida } from "@/core/shared/domain/view/material.view";

export default defineComponent({
  name: "CmpSubirPdf",
  components: { VButton, VField, VIcon, VModal, VProgressBar },
  props: {
    fase: { type: String as PropType<FaseSubida>, required: true },
    progreso: { type: Number, required: true },
    nombreArchivo: { type: String, required: true },
    tamanoArchivoMb: { type: Number, required: true },
    archivo: { type: Object as PropType<ArchivoLeido | null>, default: null },
    modelValue: { type: Boolean, default: false },
  },
  emits: {
    elegir: () => true,
    cancelar: () => true,
    usar: () => true,
    "update:modelValue": (_valor: boolean) => true,
  },
  setup(props) {
    const abierto = useModel(props, "modelValue");

    const PREFIX = "cmp-subir-pdf";

    const pegando = ref(false);

    const textoPegado = ref("");

    const cancelar = () => {
      abierto.value = false;
    };

    watch(abierto, (valor) => {
      if (!valor) {
        pegando.value = false;
        textoPegado.value = "";
      }
    });

    return { PREFIX, pegando, textoPegado, cancelar, abierto };
  },
});
