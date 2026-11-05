<template>
  <div :class="PREFIX">
    <span :class="`${PREFIX}__avatar`" aria-hidden="true">{{ alumno.nombre.charAt(0).toUpperCase() }}</span>
    <div :class="`${PREFIX}__textos`">
      <p :class="`${PREFIX}__nombre`">{{ alumno.nombre }}</p>
      <p :class="`${PREFIX}__detalle`">{{ ESTADO_ALUMNO[alumno.estado].detalle }}</p>
      <v-chip :tono="ESTADO_ALUMNO[alumno.estado].tono" :icono="ESTADO_ALUMNO[alumno.estado].icono">
        {{ ESTADO_ALUMNO[alumno.estado].texto }}
      </v-chip>
    </div>
  </div>
</template>

<script src="./cmp-alumno-item.ts" lang="ts"></script>

<style src="./cmp-alumno-item.scss" lang="scss" scoped></style>
