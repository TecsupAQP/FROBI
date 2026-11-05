<template>
  <article :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <div :class="`${PREFIX}__encabezado`">
      <span :class="`${PREFIX}__icono`" aria-hidden="true">
        <v-icon nombre="book" :tamano="32" />
      </span>
      <div>
        <h2 :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">Guía: {{ guia.titulo }}</h2>
        <p :class="`${PREFIX}__meta`">
          {{ guia.carrera }} · {{ guia.temas.length }} {{ guia.temas.length === 1 ? "tema" : "temas" }} ·
          {{ guia.minutosLectura }} min de lectura
        </p>
      </div>
    </div>
    <p :class="`${PREFIX}__descripcion`">{{ guia.descripcion }}</p>
    <ul :class="`${PREFIX}__etiquetas`" aria-label="Temas de la guía">
      <li v-for="etiqueta in guia.etiquetas" :key="etiqueta" :class="`${PREFIX}__etiqueta`">
        {{ etiqueta }}
      </li>
    </ul>
    <v-button :class="`${PREFIX}__abrir`" icono-fin="arrow" :destino="{ name: RutaEnum.GUIA }"
      >Abrir guía</v-button
    >
  </article>
</template>

<script src="./cmp-tarjeta-guia.ts" lang="ts"></script>

<style src="./cmp-tarjeta-guia.scss" lang="scss" scoped></style>
