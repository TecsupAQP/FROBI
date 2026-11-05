<template>
  <div :class="[PREFIX, `${PREFIX}--${afirmacion.estado}`]">
    <v-semaforo :estado="afirmacion.estado" />
    <p :class="`${PREFIX}__texto`">«{{ afirmacion.texto }}»</p>
    <div v-if="afirmacion.citaGuia" :class="`${PREFIX}__cita`">
      <p :class="`${PREFIX}__cita-titulo`">Tu guía dice</p>
      <p>«{{ afirmacion.citaGuia }}»</p>
    </div>
    <p :class="`${PREFIX}__motivo`">{{ afirmacion.motivo }}</p>
  </div>
</template>

<script src="./cmp-afirmacion.ts" lang="ts"></script>

<style src="./cmp-afirmacion.scss" lang="scss" scoped></style>
