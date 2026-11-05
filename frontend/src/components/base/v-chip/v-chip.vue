<template>
  <span :class="[PREFIX, `${PREFIX}--${tono}`]">
    <v-icon v-if="icono" :nombre="icono" :tamano="18" />
    <slot />
  </span>
</template>

<script src="./v-chip.ts" lang="ts"></script>

<style src="./v-chip.scss" lang="scss" scoped></style>
