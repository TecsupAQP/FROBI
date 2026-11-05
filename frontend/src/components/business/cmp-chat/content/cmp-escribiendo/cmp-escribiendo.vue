<template>
  <li :class="PREFIX" role="status">
    <span :class="`${PREFIX}__avatar`" aria-hidden="true">
      <img :src="logoIcono" alt="" width="22" height="22" />
    </span>
    <div :class="`${PREFIX}__burbuja`">
      <span :class="`${PREFIX}__puntos`" aria-hidden="true"><i></i><i></i><i></i></span>
      <span :class="`${PREFIX}__texto`">{{ estado ?? "FROBI está pensando…" }}</span>
    </div>
  </li>
</template>

<script src="./cmp-escribiendo.ts" lang="ts"></script>

<style src="./cmp-escribiendo.scss" lang="scss" scoped></style>
