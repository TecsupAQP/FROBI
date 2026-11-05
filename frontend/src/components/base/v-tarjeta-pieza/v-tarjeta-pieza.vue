<template>
  <div :class="[PREFIX, `${PREFIX}--${pieza}`]">
    <p :class="`${PREFIX}__nombre`">{{ nombrePieza(pieza) }}</p>
    <p :class="`${PREFIX}__texto`"><slot /></p>
  </div>
</template>

<script src="./v-tarjeta-pieza.ts" lang="ts"></script>

<style src="./v-tarjeta-pieza.scss" lang="scss" scoped></style>
