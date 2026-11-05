<template>
  <div ref="raiz" :class="[PREFIX, { [`${PREFIX}--abierto`]: abierto, [`${PREFIX}--error`]: error }]">
    <span :id="`${id}-etiqueta`" :class="`${PREFIX}__etiqueta`">{{ etiqueta }}</span>
    <button
      :id="id"
      ref="boton"
      type="button"
      :class="`${PREFIX}__boton`"
      aria-haspopup="listbox"
      :aria-expanded="abierto"
      :aria-labelledby="`${id}-etiqueta ${id}`"
      :aria-controls="`${id}-lista`"
      :aria-invalid="error ? 'true' : undefined"
      :aria-describedby="error ? `${id}-error` : undefined"
      @click="alternar"
      @keydown="alPresionarEnBoton"
    >
      <span :class="[`${PREFIX}__valor`, { [`${PREFIX}__valor--vacio`]: !seleccionada }]">
        {{ seleccionada?.nombre ?? placeholder }}
      </span>
      <v-icon :nombre="abierto ? 'chevu' : 'chevd'" />
    </button>
    <ul
      v-show="abierto"
      :id="`${id}-lista`"
      ref="lista"
      :class="`${PREFIX}__lista`"
      role="listbox"
      tabindex="-1"
      :aria-labelledby="`${id}-etiqueta`"
      :aria-activedescendant="activa >= 0 ? `${id}-opcion-${activa}` : undefined"
      @keydown="alPresionarEnLista"
    >
      <li
        v-for="(opcion, indice) in opciones"
        :id="`${id}-opcion-${indice}`"
        :key="opcion.id"
        role="option"
        :aria-selected="opcion.id === modelo"
        :class="[
          `${PREFIX}__opcion`,
          {
            [`${PREFIX}__opcion--activa`]: indice === activa,
            [`${PREFIX}__opcion--seleccionada`]: opcion.id === modelo,
          },
        ]"
        @click="elegir(indice)"
        @mousemove="activa = indice"
      >
        <span>{{ opcion.nombre }}</span>
        <v-icon v-if="opcion.id === modelo" nombre="check" :tamano="20" />
      </li>
    </ul>
    <p v-if="error" :id="`${id}-error`" :class="`${PREFIX}__error`">
      <v-icon nombre="alert" :tamano="20" />
      {{ error }}
    </p>
  </div>
</template>

<script src="./v-select.ts" lang="ts"></script>

<style src="./v-select.scss" lang="scss" scoped></style>
