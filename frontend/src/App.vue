<template>
  <a class="app__saltar" href="#contenido">Saltar al contenido</a>
  <router-view />
  <cmp-avisos-temporales />
</template>

<script setup lang="ts">
import CmpAvisosTemporales from "@/components/common/cmp-avisos-temporales/cmp-avisos-temporales.vue";
import useAplicarAjustes from "@/composables/common/cmp-ajustes/aplicar-ajustes.composable";

useAplicarAjustes();
</script>

<style lang="scss">
.app__saltar {
  position: absolute;
  top: $esp-8;
  left: $esp-8;
  z-index: $capa-toast;
  padding: $esp-10 $esp-16;
  border-radius: $radio-10;
  background-color: $marca-azul;
  @include texto-boton;
  color: $texto-inverso;
  transform: translateY(-200%);

  &:focus-visible {
    transform: none;
  }
}
</style>
