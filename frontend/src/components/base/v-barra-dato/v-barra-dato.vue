<template>
  <div :class="[PREFIX, `${PREFIX}--${tono}`]">
    <p :class="`${PREFIX}__fila`">
      <span :class="`${PREFIX}__etiqueta`">{{ etiqueta }}</span>
      <span :class="`${PREFIX}__valor`">{{ valorTexto }}</span>
    </p>
    <v-progress-bar
      :class="`${PREFIX}__barra`"
      :valor="valor"
      :maximo="maximo"
      :etiqueta="etiqueta"
      :texto-valor="valorTexto"
      tono="marca"
    />
  </div>
</template>

<script src="./v-barra-dato.ts" lang="ts"></script>

<style src="./v-barra-dato.scss" lang="scss" scoped></style>
