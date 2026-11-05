<template>
  <div :class="PREFIX">
    <span :id="`${id}-etiqueta`" :class="`${PREFIX}__etiqueta`">{{ etiqueta }}</span>
    <button
      :id="id"
      type="button"
      role="switch"
      :class="[`${PREFIX}__control`, { [`${PREFIX}__control--activo`]: modelo }]"
      :aria-checked="modelo"
      :aria-labelledby="`${id}-etiqueta`"
      @click="modelo = !modelo"
    >
      <span :class="`${PREFIX}__perilla`" aria-hidden="true"></span>
    </button>
  </div>
</template>

<script src="./v-switch.ts" lang="ts"></script>

<style src="./v-switch.scss" lang="scss" scoped></style>
