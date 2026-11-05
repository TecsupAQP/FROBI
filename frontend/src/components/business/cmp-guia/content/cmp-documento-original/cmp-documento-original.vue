<template>
  <section :class="[PREFIX, { [`${PREFIX}--abierto`]: abierto }]">
    <h2 :class="`${PREFIX}__encabezado`">
      <button
        type="button"
        :class="`${PREFIX}__boton`"
        :aria-expanded="abierto"
        :aria-controls="`${PREFIX}-cuerpo`"
        @click="$emit('alternar')"
      >
        <span :class="`${PREFIX}__icono`" aria-hidden="true"><v-icon nombre="file" /></span>
        <span :class="`${PREFIX}__titulo`">
          Documento original
          <span :class="`${PREFIX}__detalle`">El PDF tal como lo subiste</span>
        </span>
        <v-icon :class="`${PREFIX}__chevron`" :nombre="abierto ? 'chevu' : 'chevd'" />
      </button>
    </h2>

    <div v-if="abierto" :id="`${PREFIX}-cuerpo`" :class="`${PREFIX}__cuerpo`">
      <v-aviso v-if="error" tipo="error"
        >No pudimos abrir el documento. Inténtalo de nuevo en un momento.</v-aviso
      >
      <div v-else-if="!url" :class="`${PREFIX}__cargando`">
        <v-cargando>Abriendo el documento…</v-cargando>
      </div>
      <template v-else>
        <iframe :class="`${PREFIX}__visor`" :src="url" :title="`Documento original: ${titulo}`" />
        <a :class="`${PREFIX}__enlace`" :href="url" target="_blank" rel="noopener noreferrer">
          Abrir en otra pestaña<span class="solo-lector"> (se abre en una pestaña nueva)</span>
        </a>
      </template>
    </div>
  </section>
</template>

<script src="./cmp-documento-original.ts" lang="ts"></script>

<style src="./cmp-documento-original.scss" lang="scss" scoped></style>
