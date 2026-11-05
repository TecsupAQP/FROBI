<template>
  <section :class="PREFIX">
    <h2 :class="`${PREFIX}__encabezado`">
      <button
        type="button"
        :class="`${PREFIX}__alternar`"
        :aria-expanded="desplegada"
        :aria-controls="`${PREFIX}-piezas`"
        @click="$emit('alternar')"
      >
        <span>Así se lo pedí a la IA</span>
        <v-icon :nombre="desplegada ? 'chevu' : 'chevd'" />
      </button>
    </h2>
    <div v-show="desplegada" :id="`${PREFIX}-piezas`" :class="`${PREFIX}__cuerpo`">
      <ul :class="`${PREFIX}__piezas`" aria-label="Instrucción completa, en 4 piezas">
        <li v-for="pieza in receta" :key="pieza.pieza">
          <v-tarjeta-pieza :pieza="pieza.pieza">{{ pieza.texto }}</v-tarjeta-pieza>
        </li>
      </ul>
      <v-button variante="secundario" @click="$emit('copiar')">Copiar receta</v-button>
    </div>
  </section>
</template>

<script src="./cmp-receta-ia.ts" lang="ts"></script>

<style src="./cmp-receta-ia.scss" lang="scss" scoped></style>
