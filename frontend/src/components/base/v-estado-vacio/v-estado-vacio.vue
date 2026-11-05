<template>
  <section :class="PREFIX" :aria-labelledby="`${PREFIX}-${icono}`">
    <span :class="`${PREFIX}__icono`" aria-hidden="true">
      <v-icon :nombre="icono" :tamano="40" />
    </span>
    <h2 :id="`${PREFIX}-${icono}`" :class="`${PREFIX}__titulo`">{{ titulo }}</h2>
    <p :class="`${PREFIX}__texto`">{{ texto }}</p>
    <slot />
  </section>
</template>

<script src="./v-estado-vacio.ts" lang="ts"></script>

<style src="./v-estado-vacio.scss" lang="scss" scoped></style>
