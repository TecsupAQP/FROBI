<template>
  <section :class="PREFIX" aria-label="Qué es FROBI">
    <span :class="`${PREFIX}__logo`"><v-logo :alto="48" /></span>
    <div :class="`${PREFIX}__centro`">
      <p :class="`${PREFIX}__lema`">Aprende con IA, aprende a usar IA.</p>
      <p :class="`${PREFIX}__descripcion`">
        Convierte tu guía de clase en el formato que necesitas y descubre cómo se lo pides a la IA.
      </p>
      <div :class="`${PREFIX}__receta`">
        <p :class="`${PREFIX}__receta-titulo`">Así se lo pedí a la IA</p>
        <ul :class="`${PREFIX}__piezas`">
          <li v-for="pieza in receta" :key="pieza.pieza" :class="`${PREFIX}__pieza`">
            <v-chip-pieza :class="`${PREFIX}__chip`" :pieza="pieza.pieza" />
            <span>{{ pieza.texto }}</span>
          </li>
        </ul>
      </div>
    </div>
    <div :class="`${PREFIX}__pie`">
      <p>Hack4Edu Arequipa 2026 · Reto 03</p>
      <span :class="`${PREFIX}__reto`">
        <img :src="LOGO_RETO" alt="Reto ProFuturo" width="2000" height="667" decoding="async" />
      </span>
    </div>
  </section>
</template>

<script src="./cmp-panel-marca.ts" lang="ts"></script>

<style src="./cmp-panel-marca.scss" lang="scss" scoped></style>
