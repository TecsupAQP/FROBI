<template>
  <section :class="[PREFIX, { [`${PREFIX}--abierto`]: abierto }]">
    <h2 :class="`${PREFIX}__encabezado`">
      <button
        type="button"
        :class="`${PREFIX}__boton`"
        :aria-expanded="abierto"
        :aria-controls="`${PREFIX}-${tema.id}`"
        @click="$emit('alternar', tema.id)"
      >
        <span :class="`${PREFIX}__numero`" aria-hidden="true">{{ tema.numero }}</span>
        <span :class="`${PREFIX}__titulo`"
          ><span class="solo-lector">Tema {{ tema.numero }}: </span>{{ tema.titulo }}</span
        >
        <v-icon :class="`${PREFIX}__chevron`" :nombre="abierto ? 'chevu' : 'chevd'" />
      </button>
    </h2>
    <div v-show="abierto" :id="`${PREFIX}-${tema.id}`" :class="`${PREFIX}__cuerpo`">
      <span :class="`${PREFIX}__etiqueta`">Texto original de la guía</span>
      <p :class="`${PREFIX}__texto`">{{ tema.textoOriginal }}</p>
    </div>
  </section>
</template>

<script src="./cmp-tema.ts" lang="ts"></script>

<style src="./cmp-tema.scss" lang="scss" scoped></style>
