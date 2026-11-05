<template>
  <div
    :class="[PREFIX, `${PREFIX}--${tono}`]"
    role="progressbar"
    :aria-valuenow="valorSeguro"
    aria-valuemin="0"
    :aria-valuemax="maximo"
    :aria-label="etiqueta"
    :aria-valuetext="textoValor"
  >
    <span :class="`${PREFIX}__relleno`" :style="{ width: `${(valorSeguro / maximo) * 100}%` }"></span>
  </div>
</template>

<script src="./v-progress-bar.ts" lang="ts"></script>

<style src="./v-progress-bar.scss" lang="scss" scoped></style>
