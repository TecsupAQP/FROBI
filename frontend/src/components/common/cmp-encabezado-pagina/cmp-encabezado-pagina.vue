<template>
  <header :class="PREFIX">
    <div :class="`${PREFIX}__textos`">
      <router-link v-if="volver" :to="volver.destino" :class="`${PREFIX}__volver`">
        <v-icon nombre="chevl" :tamano="20" />
        {{ volver.texto }}
      </router-link>
      <p v-if="antetitulo" :class="`${PREFIX}__antetitulo`">{{ antetitulo }}</p>
      <h1 :class="`${PREFIX}__titulo`">{{ titulo }}</h1>
      <p v-if="descripcion" :class="`${PREFIX}__descripcion`">{{ descripcion }}</p>
    </div>
    <div v-if="$slots.acciones" :class="`${PREFIX}__acciones`">
      <slot name="acciones" />
    </div>
  </header>
</template>

<script src="./cmp-encabezado-pagina.ts" lang="ts"></script>

<style src="./cmp-encabezado-pagina.scss" lang="scss" scoped></style>
