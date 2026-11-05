<template>
  <span :class="[PREFIX, `${PREFIX}--${pieza}`, { [`${PREFIX}--compacto`]: compacto }]">
    <slot>{{ nombrePieza(pieza) }}</slot>
  </span>
</template>

<script src="./v-chip-pieza.ts" lang="ts"></script>

<style src="./v-chip-pieza.scss" lang="scss" scoped></style>
