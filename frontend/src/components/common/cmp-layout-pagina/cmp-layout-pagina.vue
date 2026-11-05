<template>
  <div :class="[PREFIX, { [`${PREFIX}--con-barra-inferior`]: $slots['barra-inferior'] }]">
    <cmp-barra-superior />
    <main id="contenido" :class="`${PREFIX}__principal`" tabindex="-1">
      <slot />
    </main>
    <div v-if="$slots['barra-inferior']" :class="`${PREFIX}__barra-inferior`">
      <slot name="barra-inferior" />
    </div>
    <cmp-recorrido />
  </div>
</template>

<script src="./cmp-layout-pagina.ts" lang="ts"></script>

<style src="./cmp-layout-pagina.scss" lang="scss" scoped></style>
