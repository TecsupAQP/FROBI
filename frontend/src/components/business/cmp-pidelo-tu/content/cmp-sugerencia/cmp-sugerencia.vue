<template>
  <section :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <h2 :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">
      <v-icon nombre="bulb" />
      Sugerencia
    </h2>
    <p>{{ sugerencia.texto }} Por ejemplo: «{{ sugerencia.ejemplo }}»</p>
    <v-cargando v-if="ocupado">Mejorando tu instrucción…</v-cargando>
    <div v-else :class="`${PREFIX}__acciones`">
      <v-button @click="$emit('mejorar')">Mejorar mi instrucción</v-button>
      <v-button variante="secundario" @click="$emit('anadir')">Añadir el ejemplo</v-button>
    </div>
  </section>
</template>

<script src="./cmp-sugerencia.ts" lang="ts"></script>

<style src="./cmp-sugerencia.scss" lang="scss" scoped></style>
