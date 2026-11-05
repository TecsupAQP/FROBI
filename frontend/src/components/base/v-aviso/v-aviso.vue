<template>
  <div :class="[PREFIX, `${PREFIX}--${tipo}`]" :role="tipo === 'error' ? 'alert' : undefined">
    <v-icon :nombre="icono ?? ICONO_POR_TIPO[tipo]" :tamano="tipo === 'nota' ? 20 : 22" />
    <div :class="`${PREFIX}__texto`"><slot /></div>
  </div>
</template>

<script src="./v-aviso.ts" lang="ts"></script>

<style src="./v-aviso.scss" lang="scss" scoped></style>
