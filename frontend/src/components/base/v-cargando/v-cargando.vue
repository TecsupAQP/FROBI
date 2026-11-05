<template>
  <div :class="PREFIX" role="status" aria-live="polite">
    <span :class="`${PREFIX}__puntos`" aria-hidden="true">
      <span :class="`${PREFIX}__punto`"></span>
      <span :class="`${PREFIX}__punto`"></span>
      <span :class="`${PREFIX}__punto`"></span>
    </span>
    <span :class="`${PREFIX}__texto`"><slot>Cargando…</slot></span>
  </div>
</template>

<script src="./v-cargando.ts" lang="ts"></script>

<style src="./v-cargando.scss" lang="scss" scoped></style>
