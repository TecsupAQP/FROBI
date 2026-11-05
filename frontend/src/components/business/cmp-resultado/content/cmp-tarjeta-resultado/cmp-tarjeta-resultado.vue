<template>
  <section :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <header :class="`${PREFIX}__encabezado`">
      <span :class="`${PREFIX}__icono`">
        <v-icon :nombre="formato.icono" :tamano="26" />
      </span>
      <div>
        <h2 :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">{{ formato.nombre }}</h2>
        <p :class="`${PREFIX}__subtitulo`">{{ tema }}</p>
      </div>
    </header>
    <slot />
  </section>
</template>

<script src="./cmp-tarjeta-resultado.ts" lang="ts"></script>

<style src="./cmp-tarjeta-resultado.scss" lang="scss" scoped></style>
