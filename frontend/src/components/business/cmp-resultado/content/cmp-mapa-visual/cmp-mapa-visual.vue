<template>
  <div :class="PREFIX">
    <figure :class="`${PREFIX}__diagrama`">
      <figcaption class="solo-lector">Mapa de conceptos de {{ contenido.conceptoCentral }}</figcaption>
      <p :class="`${PREFIX}__central`">{{ contenido.conceptoCentral }}</p>
      <ul :class="`${PREFIX}__ramas`">
        <li v-for="nodo in contenido.nodos" :key="nodo.titulo" :class="`${PREFIX}__rama`">
          <div :class="`${PREFIX}__nodo`">
            <p :class="`${PREFIX}__nodo-titulo`">{{ nodo.titulo }}</p>
            <p :class="`${PREFIX}__nodo-detalle`">{{ nodo.detalle }}</p>
          </div>
        </li>
      </ul>
    </figure>
    <v-aviso v-if="contenido.usos" tipo="info">{{ contenido.usos }}</v-aviso>
  </div>
</template>

<script src="./cmp-mapa-visual.ts" lang="ts"></script>

<style src="./cmp-mapa-visual.scss" lang="scss" scoped></style>
