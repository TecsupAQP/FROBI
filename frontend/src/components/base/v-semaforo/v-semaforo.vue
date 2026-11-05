<template>
  <span :class="[PREFIX, `${PREFIX}--${estado}`]">
    <v-icon :nombre="SEMAFORO[estado].icono" :tamano="20" />
    <slot>{{ SEMAFORO[estado].texto }}</slot>
  </span>
</template>

<script src="./v-semaforo.ts" lang="ts"></script>

<style src="./v-semaforo.scss" lang="scss" scoped></style>
