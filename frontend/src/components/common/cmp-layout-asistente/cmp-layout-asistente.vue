<template>
  <div :class="PREFIX">
    <header :class="`${PREFIX}__cabecera`">
      <v-logo :class="`${PREFIX}__logo-movil`" variante="icono" :alto="36" />
      <v-logo :class="`${PREFIX}__logo-escritorio`" :alto="40" />
      <!-- "Omitir" siempre visible en cada paso del asistente. -->
      <button type="button" :class="`${PREFIX}__omitir`" @click="$emit('omitir')">{{ textoOmitir }}</button>
    </header>
    <main id="contenido" :class="`${PREFIX}__principal`" tabindex="-1">
      <div :class="`${PREFIX}__columna`">
        <slot />
      </div>
    </main>
  </div>
</template>

<script src="./cmp-layout-asistente.ts" lang="ts"></script>

<style src="./cmp-layout-asistente.scss" lang="scss" scoped></style>
