<template>
  <section :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <div>
      <h2 :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">Qué tan completa está</h2>
      <p :class="`${PREFIX}__puntaje`">
        Puntaje: {{ evaluacion.presentes }} de {{ evaluacion.total }} piezas
      </p>
    </div>
    <ul :class="`${PREFIX}__lista`">
      <li v-for="item in evaluacion.piezas" :key="item.pieza" :class="`${PREFIX}__pieza`">
        <div :class="`${PREFIX}__fila`">
          <v-chip-pieza :pieza="item.pieza" compacto />
          <span :class="[`${PREFIX}__estado`, `${PREFIX}__estado--${item.presente ? 'presente' : 'falta'}`]">
            <v-icon :nombre="item.presente ? 'check' : 'x'" :tamano="20" />
            {{ item.presente ? "Presente" : "Falta" }}
          </span>
        </div>
        <span :class="[`${PREFIX}__barra`, `${PREFIX}__barra--${item.pieza}`]" aria-hidden="true">
          <span :class="`${PREFIX}__relleno`" :style="{ width: item.presente ? '100%' : '0%' }"></span>
        </span>
        <p :class="`${PREFIX}__comentario`">{{ item.comentario }}</p>
      </li>
    </ul>
  </section>
</template>

<script src="./cmp-puntaje-piezas.ts" lang="ts"></script>

<style src="./cmp-puntaje-piezas.scss" lang="scss" scoped></style>
