<template>
  <div :class="PREFIX">
    <div
      :class="`${PREFIX}__segmentos`"
      role="progressbar"
      :aria-valuenow="actual"
      aria-valuemin="1"
      :aria-valuemax="total"
      :aria-label="`Paso ${actual} de ${total}`"
    >
      <span
        v-for="numero in total"
        :key="numero"
        :class="[`${PREFIX}__segmento`, { [`${PREFIX}__segmento--hecho`]: numero <= actual }]"
      ></span>
    </div>
    <p :class="`${PREFIX}__texto`">
      Paso {{ actual }} de {{ total }}<template v-if="nota"> · {{ nota }}</template>
    </p>
  </div>
</template>

<script src="./v-pasos.ts" lang="ts"></script>

<style src="./v-pasos.scss" lang="scss" scoped></style>
