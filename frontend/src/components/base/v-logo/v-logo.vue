<template>
  <span :class="[PREFIX, `${PREFIX}--${variante}`]" :style="{ '--alto': `${alto}px` }">
    <img
      v-if="variante === 'horizontal'"
      :class="`${PREFIX}__imagen`"
      :src="logoHorizontal"
      alt="FROBI"
      :height="alto"
      :width="Math.round(alto * PROPORCION_HORIZONTAL)"
    />
    <template v-else>
      <img
        :class="`${PREFIX}__imagen`"
        :src="logoIcono"
        :alt="variante === 'icono' ? 'FROBI' : ''"
        :height="alto"
        :width="Math.round(alto * PROPORCION_ICONO)"
      />
      <!-- Sobre fondo marino el texto del logo horizontal no se lee: ícono + nombre en blanco. -->
      <span v-if="variante === 'inverso'" :class="`${PREFIX}__nombre`">FROBI</span>
    </template>
  </span>
</template>

<script src="./v-logo.ts" lang="ts"></script>

<style src="./v-logo.scss" lang="scss" scoped></style>
