<template>
  <div :class="PREFIX">
    <header :class="`${PREFIX}__cabecera`">
      <router-link :to="{ name: RutaEnum.INICIO }" aria-label="FROBI, ir al inicio">
        <v-logo :alto="40" />
      </router-link>
      <router-link :class="`${PREFIX}__volver`" :to="{ name: RutaEnum.INICIO }">Ir a FROBI</router-link>
    </header>
    <main id="contenido" :class="`${PREFIX}__principal`" tabindex="-1">
      <slot />
    </main>
  </div>
</template>

<script src="./cmp-layout-presentacion.ts" lang="ts"></script>

<style src="./cmp-layout-presentacion.scss" lang="scss" scoped></style>
