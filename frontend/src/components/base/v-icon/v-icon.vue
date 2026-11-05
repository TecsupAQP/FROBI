<!-- eslint-disable vue/no-v-html -- el contenido sale de iconos.constant.ts (generado), nunca de datos del usuario -->
<template>
  <svg
    :class="PREFIX"
    :width="tamano"
    :height="tamano"
    :viewBox="definicion.viewBox"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    :role="etiqueta ? 'img' : undefined"
    :aria-label="etiqueta"
    :aria-hidden="etiqueta ? undefined : 'true'"
    focusable="false"
    v-html="definicion.contenido"
  ></svg>
</template>

<script src="./v-icon.ts" lang="ts"></script>

<style src="./v-icon.scss" lang="scss" scoped></style>
