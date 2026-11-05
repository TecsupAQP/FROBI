<template>
  <section :class="PREFIX" :aria-labelledby="`${PREFIX}-${seccion.id}`">
    <div :class="`${PREFIX}__encabezado`">
      <span :class="`${PREFIX}__numero`" aria-hidden="true">{{ seccion.numero }}</span>
      <h2 :id="`${PREFIX}-${seccion.id}`" :class="`${PREFIX}__titulo`">{{ seccion.titulo }}</h2>
      <v-semaforo v-if="seccion.estadoSeccion" :estado="seccion.estadoSeccion.estado">
        {{ seccion.estadoSeccion.texto }}
      </v-semaforo>
    </div>
    <p v-if="seccion.texto" :class="`${PREFIX}__texto`">{{ seccion.texto }}</p>
    <ul
      v-if="seccion.afirmaciones.length"
      :class="`${PREFIX}__afirmaciones`"
      aria-label="Afirmaciones para revisar"
    >
      <li v-for="afirmacion in seccion.afirmaciones" :key="afirmacion.id">
        <cmp-afirmacion :afirmacion="afirmacion" />
      </li>
    </ul>
  </section>
</template>

<script src="./cmp-seccion-revisada.ts" lang="ts"></script>

<style src="./cmp-seccion-revisada.scss" lang="scss" scoped></style>
