<template>
  <section :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <div :class="`${PREFIX}__cabecera`">
      <span :class="`${PREFIX}__contador`">Tema {{ actual.numero }} de {{ temas.length }}</span>
      <span v-if="actual.paginas" :class="`${PREFIX}__paginas`">
        <v-icon nombre="file" :tamano="18" />
        {{ actual.paginas }}
      </span>
    </div>

    <div :class="`${PREFIX}__actual`">
      <button
        type="button"
        :class="`${PREFIX}__paso`"
        :disabled="indice === 0"
        aria-label="Tema anterior"
        @click="mover(-1)"
      >
        <v-icon nombre="chevl" />
      </button>
      <div :class="`${PREFIX}__texto`" aria-live="polite">
        <h2 :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">{{ actual.titulo }}</h2>
        <p :class="`${PREFIX}__resumen`">{{ resumen }}</p>
      </div>
      <button
        type="button"
        :class="`${PREFIX}__paso`"
        :disabled="indice === temas.length - 1"
        aria-label="Tema siguiente"
        @click="mover(1)"
      >
        <v-icon nombre="chev" />
      </button>
    </div>

    <v-select
      :id="`${PREFIX}-lista`"
      etiqueta="Ir a otro tema"
      :opciones="opciones"
      :model-value="actual.id"
      @update:model-value="$emit('elegir', $event)"
    />
  </section>
</template>

<script src="./cmp-elegir-tema.ts" lang="ts"></script>

<style src="./cmp-elegir-tema.scss" lang="scss" scoped></style>
