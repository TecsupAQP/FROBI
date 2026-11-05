<template>
  <label :class="[PREFIX, { [`${PREFIX}--seleccionada`]: modelo === valor, [`${PREFIX}--error`]: error }]">
    <input
      v-model="modelo"
      :class="`${PREFIX}__control`"
      type="radio"
      :name="nombre"
      :value="valor"
      :aria-invalid="error ? 'true' : undefined"
      :aria-describedby="descripcion"
    />
    <span :class="`${PREFIX}__circulo`" aria-hidden="true"></span>
    <span :class="`${PREFIX}__texto`"><slot /></span>
  </label>
</template>

<script src="./v-radio-opcion.ts" lang="ts"></script>

<style src="./v-radio-opcion.scss" lang="scss" scoped></style>
