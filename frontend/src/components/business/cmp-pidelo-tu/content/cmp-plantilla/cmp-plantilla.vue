<template>
  <section :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <h2 :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">
      <v-icon nombre="file" />
      Plantilla (opcional)
    </h2>
    <p>Completa los espacios. Cada parte tiene su color.</p>
    <ul :class="`${PREFIX}__piezas`">
      <li v-for="pieza in plantilla" :key="pieza.pieza">
        <v-tarjeta-pieza :pieza="pieza.pieza">{{ pieza.texto }}</v-tarjeta-pieza>
      </li>
    </ul>
    <v-button variante="secundario" @click="$emit('usar')">Usar plantilla</v-button>
  </section>
</template>

<script src="./cmp-plantilla.ts" lang="ts"></script>

<style src="./cmp-plantilla.scss" lang="scss" scoped></style>
