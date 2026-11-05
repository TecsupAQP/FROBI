<template>
  <div :class="PREFIX">
    <figure v-if="!fallo" :class="`${PREFIX}__figura`">
      <div :class="`${PREFIX}__barra`" role="toolbar" aria-label="Controles del mapa">
        <p :class="`${PREFIX}__ayuda`">
          Toca un círculo para abrir o cerrar una rama. Arrastra para moverte.
        </p>
        <div :class="`${PREFIX}__botones`">
          <button type="button" :class="`${PREFIX}__control`" aria-label="Acercar" @click="acercar">+</button>
          <button type="button" :class="`${PREFIX}__control`" aria-label="Alejar" @click="alejar">−</button>
          <button type="button" :class="`${PREFIX}__control ${PREFIX}__control--texto`" @click="ajustar">
            Ver todo
          </button>
        </div>
      </div>
      <!-- El SVG es visual; la misma información está en la lista de abajo. -->
      <svg ref="lienzo" :class="`${PREFIX}__lienzo`" aria-hidden="true" focusable="false"></svg>
      <figcaption class="solo-lector">Mapa de conceptos de {{ contenido.conceptoCentral }}.</figcaption>
    </figure>

    <details :class="`${PREFIX}__lista`" :open="fallo">
      <summary :class="`${PREFIX}__resumen`">
        <v-icon nombre="type" :tamano="20" />
        Ver el mapa como lista
      </summary>
      <h3 :class="`${PREFIX}__central`">{{ contenido.conceptoCentral }}</h3>
      <ul :class="`${PREFIX}__ramas`">
        <li v-for="rama in contenido.nodos" :key="rama.titulo" :class="`${PREFIX}__rama`">
          <p :class="`${PREFIX}__rama-titulo`">{{ rama.titulo }}</p>
          <p v-if="rama.detalle" :class="`${PREFIX}__rama-detalle`">{{ rama.detalle }}</p>
          <ul v-if="rama.puntos.length" :class="`${PREFIX}__puntos`">
            <li v-for="item in rama.puntos" :key="item">{{ item }}</li>
          </ul>
        </li>
      </ul>
    </details>

    <v-aviso v-if="contenido.usos" tipo="info">{{ contenido.usos }}</v-aviso>
  </div>
</template>

<script src="./cmp-mapa-visual.ts" lang="ts"></script>

<style src="./cmp-mapa-visual.scss" lang="scss" scoped></style>
