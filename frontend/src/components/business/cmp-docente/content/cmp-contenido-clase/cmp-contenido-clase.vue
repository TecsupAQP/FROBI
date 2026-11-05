<template>
  <section :class="PREFIX" aria-labelledby="contenido-clase-titulo">
    <div :class="`${PREFIX}__cabecera`">
      <div>
        <h2 id="contenido-clase-titulo" :class="`${PREFIX}__titulo`">Contenido de la clase</h2>
        <p :class="`${PREFIX}__secundario`">
          Tus alumnos lo ven en su Inicio y lo estudian en el formato que les sirva.
        </p>
      </div>
      <v-button icono="upload" variante="secundario" :deshabilitado="subiendo" @click="abrirSelector">
        {{ subiendo ? "Subiendo…" : "Subir material" }}
      </v-button>
    </div>

    <p v-if="error" :class="`${PREFIX}__error`" role="alert">
      <v-icon nombre="alert" :tamano="20" />
      {{ error }}
    </p>

    <p v-if="!materiales.length" :class="`${PREFIX}__vacio`">
      Todavía no subiste material. Sube la guía o los PDF de tu curso.
    </p>
    <ul v-else :class="`${PREFIX}__lista`" aria-live="polite">
      <li v-for="material in materiales" :key="material.id" :class="`${PREFIX}__material`">
        <span :class="`${PREFIX}__icono`" aria-hidden="true"><v-icon nombre="file" :tamano="22" /></span>
        <div :class="`${PREFIX}__textos`">
          <p :class="`${PREFIX}__nombre`">{{ material.titulo }}</p>
          <p :class="`${PREFIX}__fecha`">Subido el {{ formatearFecha(material.fecha) }}</p>
          <p :class="`${PREFIX}__vista`">{{ material.vistaPrevia }}</p>
        </div>
      </li>
    </ul>

    <input
      ref="selector"
      class="solo-lector"
      type="file"
      accept="application/pdf,.pdf"
      tabindex="-1"
      aria-hidden="true"
      @change="alElegir"
    />
  </section>
</template>

<script src="./cmp-contenido-clase.ts" lang="ts"></script>

<style src="./cmp-contenido-clase.scss" lang="scss" scoped></style>
