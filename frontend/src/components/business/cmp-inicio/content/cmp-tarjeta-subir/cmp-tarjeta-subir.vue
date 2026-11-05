<template>
  <aside :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <h2 :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">¿Tienes tu propia guía?</h2>
    <p :class="`${PREFIX}__texto`">Sube un PDF de tu curso y la adaptamos a tu manera de aprender.</p>
    <v-button variante="secundario" icono="upload" bloque aria-haspopup="dialog" @click="$emit('subir')">
      Subir mi PDF
    </v-button>
  </aside>
</template>

<script src="./cmp-tarjeta-subir.ts" lang="ts"></script>

<style src="./cmp-tarjeta-subir.scss" lang="scss" scoped></style>
