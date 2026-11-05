<template>
  <div :class="PREFIX">
    <button
      type="button"
      :class="[`${PREFIX}__boton`, `${PREFIX}__boton--${tono}`]"
      :aria-pressed="hablando"
      @click="alternar"
    >
      <v-icon nombre="headphones" :tamano="22" />
      {{ hablando ? "Detener" : texto }}
    </button>
    <p v-if="sinVoz" :class="`${PREFIX}__aviso`" role="status">
      Tu navegador no puede leer en voz alta. El texto está en pantalla.
    </p>
  </div>
</template>

<script src="./v-boton-escuchar.ts" lang="ts"></script>

<style src="./v-boton-escuchar.scss" lang="scss" scoped></style>
