import { computed, defineComponent } from "vue";
import { useRoute } from "vue-router";
import CmpAsistente from "@/components/business/cmp-asistente/cmp-asistente.vue";

export default defineComponent({
  name: "VwAsistente",
  components: { CmpAsistente },
  setup() {
    const route = useRoute();

    const paso = computed(() => {
      const numero = Number(route.params.paso);
      return numero >= 1 && numero <= 3 ? numero : 1;
    });

    return { paso };
  },
});
