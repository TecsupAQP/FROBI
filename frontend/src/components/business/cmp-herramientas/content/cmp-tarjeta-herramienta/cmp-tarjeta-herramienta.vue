<template>
  <article :class="PREFIX" :aria-labelledby="`${PREFIX}-${herramienta.id}`">
    <div :class="`${PREFIX}__encabezado`">
      <span :class="`${PREFIX}__icono`" aria-hidden="true">
        <v-icon :nombre="herramienta.icono" :tamano="26" />
      </span>
      <div>
        <h3 :id="`${PREFIX}-${herramienta.id}`" :class="`${PREFIX}__nombre`">{{ herramienta.nombre }}</h3>
        <p :class="`${PREFIX}__para-que`">{{ herramienta.paraQue }}</p>
      </div>
    </div>
    <p :class="`${PREFIX}__uso`">
      <v-icon :class="`${PREFIX}__si`" nombre="check" :tamano="20" />
      <span>Úsala para: {{ herramienta.usala }}</span>
    </p>
    <p :class="`${PREFIX}__uso`">
      <v-icon :class="`${PREFIX}__no`" nombre="xc" :tamano="20" />
      <span>No la uses para: {{ herramienta.noLaUses }}</span>
    </p>
  </article>
</template>

<script src="./cmp-tarjeta-herramienta.ts" lang="ts"></script>

<style src="./cmp-tarjeta-herramienta.scss" lang="scss" scoped></style>
