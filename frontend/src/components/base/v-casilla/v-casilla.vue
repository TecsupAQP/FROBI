<template>
  <label :class="[PREFIX, { [`${PREFIX}--marcada`]: modelo }]">
    <input v-model="modelo" :class="`${PREFIX}__control`" type="checkbox" />
    <span :class="`${PREFIX}__caja`" aria-hidden="true">
      <v-icon v-if="modelo" nombre="check" :tamano="20" />
    </span>
    <v-icon v-if="icono" :class="`${PREFIX}__icono`" :nombre="icono" :tamano="26" />
    <span :class="`${PREFIX}__textos`">
      <span :class="`${PREFIX}__titulo`"><slot /></span>
      <span v-if="descripcion" :class="`${PREFIX}__descripcion`">{{ descripcion }}</span>
    </span>
  </label>
</template>

<script src="./v-casilla.ts" lang="ts"></script>

<style src="./v-casilla.scss" lang="scss" scoped></style>
