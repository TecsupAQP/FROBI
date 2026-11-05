<template>
  <section :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <h2 :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">
      <v-icon nombre="bulb" />
      Resultado de la mejorada
    </h2>
    <p v-for="parrafo in resultado" :key="parrafo">{{ parrafo }}</p>
    <div :class="`${PREFIX}__acciones`">
      <v-button variante="secundario" @click="$emit('copiar')">Copiar receta</v-button>
      <v-button @click="$emit('probar')">Probar otra instrucción</v-button>
    </div>
    <v-aviso tipo="nota">La IA puede equivocarse; contrasta con tu guía.</v-aviso>
  </section>
</template>

<script src="./cmp-resultado-mejorada.ts" lang="ts"></script>

<style src="./cmp-resultado-mejorada.scss" lang="scss" scoped></style>
