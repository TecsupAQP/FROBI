<template>
  <div :class="PREFIX">
    <section :class="`${PREFIX}__tuya`" :aria-labelledby="`${PREFIX}-tuya`">
      <div :class="`${PREFIX}__encabezado`">
        <h2 :id="`${PREFIX}-tuya`" :class="`${PREFIX}__titulo`">Tu instrucción</h2>
        <p :class="`${PREFIX}__conteo ${PREFIX}__conteo--falta`">
          {{ evaluacion.presentes }} de {{ evaluacion.total }} piezas
        </p>
      </div>
      <p :class="`${PREFIX}__original`">{{ evaluacion.instruccion }}</p>
      <ul :class="`${PREFIX}__faltan`" aria-label="Piezas que faltaban">
        <li v-for="item in faltantes" :key="item.pieza" :class="`${PREFIX}__falta`">
          <v-icon nombre="x" :tamano="20" />
          <v-chip-pieza :pieza="item.pieza" compacto />
          <span>Falta</span>
        </li>
      </ul>
    </section>

    <section :class="`${PREFIX}__mejorada`" :aria-labelledby="`${PREFIX}-mejorada`">
      <div :class="`${PREFIX}__encabezado`">
        <h2 :id="`${PREFIX}-mejorada`" :class="`${PREFIX}__titulo`">Instrucción mejorada</h2>
        <p :class="`${PREFIX}__conteo ${PREFIX}__conteo--completa`">
          {{ mejorada.receta.length }} de {{ evaluacion.total }} piezas
        </p>
      </div>
      <ul :class="`${PREFIX}__piezas`">
        <li v-for="pieza in mejorada.receta" :key="pieza.pieza">
          <v-tarjeta-pieza :pieza="pieza.pieza">{{ pieza.texto }}</v-tarjeta-pieza>
        </li>
      </ul>
    </section>
  </div>
</template>

<script src="./cmp-comparacion.ts" lang="ts"></script>

<style src="./cmp-comparacion.scss" lang="scss" scoped></style>
