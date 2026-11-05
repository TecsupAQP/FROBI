<template>
  <router-link
    v-if="visible"
    :to="{ name: RutaEnum.CHAT }"
    :class="[PREFIX, { [`${PREFIX}--elevado`]: elevado }]"
    aria-label="Pregúntale a FROBI"
  >
    <span :class="`${PREFIX}__icono`" aria-hidden="true"><v-icon nombre="spark" :tamano="24" /></span>
    <span :class="`${PREFIX}__texto`" aria-hidden="true">Pregúntale a FROBI</span>
  </router-link>
</template>

<script src="./cmp-boton-asistente.ts" lang="ts"></script>

<style src="./cmp-boton-asistente.scss" lang="scss" scoped></style>
