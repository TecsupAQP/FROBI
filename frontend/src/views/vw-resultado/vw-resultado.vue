<template>
  <cmp-layout-pagina>
    <cmp-resultado :key="reintentos" tema-id="tema-1" :formato="formato" @reintentar="reintentos++" />
    <template #barra-inferior>
      <v-button :class="`${PREFIX}__pidelo`" :destino="{ name: RutaEnum.PIDELO_TU }">Pídelo tú</v-button>
    </template>
  </cmp-layout-pagina>
</template>

<script src="./vw-resultado.ts" lang="ts"></script>

<style src="./vw-resultado.scss" lang="scss" scoped></style>
