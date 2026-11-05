<template>
  <div :class="PREFIX">
    <v-chip tono="marino" :class="`${PREFIX}__paso`">Paso 2 · Docente y estudiante</v-chip>
    <cmp-encabezado-pagina
      titulo="La IA es una ayudante, no un atajo"
      descripcion="Tres ideas para empezar. Dura menos de un minuto y puedes omitirla."
    />

    <ol :class="`${PREFIX}__ideas`">
      <li v-for="(idea, indice) in IDEAS" :key="idea.titulo" :class="`${PREFIX}__idea`">
        <h2 :class="`${PREFIX}__idea-titulo`">
          <span :class="`${PREFIX}__numero`" aria-hidden="true">{{ indice + 1 }}</span>
          {{ idea.titulo }}
        </h2>
        <p :class="`${PREFIX}__idea-texto`">{{ idea.texto }}</p>
        <ul v-if="idea.piezas" :class="`${PREFIX}__piezas`" aria-label="Las 4 piezas de una instrucción">
          <li v-for="pieza in PIEZAS" :key="pieza.id"><v-chip-pieza :pieza="pieza.id" compacto /></li>
        </ul>
      </li>
    </ol>

    <div :class="`${PREFIX}__acciones`">
      <v-button @click="seguir">Empezar</v-button>
      <!-- La introducción es omitible: el botón está siempre visible. -->
      <v-button variante="secundario" @click="seguir">Omitir introducción</v-button>
    </div>
  </div>
</template>

<script src="./cmp-intro.ts" lang="ts"></script>

<style src="./cmp-intro.scss" lang="scss" scoped></style>
