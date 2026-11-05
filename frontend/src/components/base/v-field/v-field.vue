<template>
  <div :class="[PREFIX, `${PREFIX}--${tamano}`, { [`${PREFIX}--error`]: error }]">
    <label :class="`${PREFIX}__etiqueta`" :for="id">{{ etiqueta }}</label>
    <div :class="`${PREFIX}__entrada`">
      <textarea
        v-if="multilinea"
        :id="id"
        v-model="modelo"
        :class="`${PREFIX}__control ${PREFIX}__control--multilinea`"
        :placeholder="placeholder"
        :rows="filas"
        :aria-invalid="error ? 'true' : undefined"
        :aria-describedby="descripcionId"
      ></textarea>
      <input
        v-else
        :id="id"
        v-model="modelo"
        :class="`${PREFIX}__control`"
        :type="tipo"
        :placeholder="placeholder"
        :autocomplete="autocompletar"
        :aria-invalid="error ? 'true' : undefined"
        :aria-describedby="descripcionId"
      />
    </div>
    <p v-if="error" :id="`${id}-error`" :class="`${PREFIX}__error`">
      <v-icon nombre="alert" :tamano="20" />
      {{ error }}
    </p>
    <p v-else-if="ayuda" :id="`${id}-ayuda`" :class="`${PREFIX}__ayuda`">{{ ayuda }}</p>
  </div>
</template>

<script src="./v-field.ts" lang="ts"></script>

<style src="./v-field.scss" lang="scss" scoped></style>
