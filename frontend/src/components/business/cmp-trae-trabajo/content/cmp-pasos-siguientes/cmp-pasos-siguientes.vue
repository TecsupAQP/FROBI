<template>
  <aside :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <h2 :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">Qué pasa después</h2>
    <ol :class="`${PREFIX}__pasos`">
      <li v-for="(paso, indice) in PASOS" :key="paso" :class="`${PREFIX}__paso`">
        <span :class="`${PREFIX}__numero`" aria-hidden="true">{{ indice + 1 }}</span>
        <span>{{ paso }}</span>
      </li>
    </ol>
    <div :class="`${PREFIX}__privacidad`">
      <v-icon nombre="shield" :tamano="22" />
      <p>Tu material no se usa para otros fines y no pedimos datos personales.</p>
    </div>
  </aside>
</template>

<script src="./cmp-pasos-siguientes.ts" lang="ts"></script>

<style src="./cmp-pasos-siguientes.scss" lang="scss" scoped></style>
