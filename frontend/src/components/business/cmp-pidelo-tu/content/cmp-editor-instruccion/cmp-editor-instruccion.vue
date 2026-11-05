<template>
  <section :class="[PREFIX, { [`${PREFIX}--compacto`]: compacto }]">
    <label :for="`${PREFIX}-texto`" :class="`${PREFIX}__etiqueta`">{{ etiqueta }}</label>
    <textarea
      :id="`${PREFIX}-texto`"
      v-model="modelo"
      :class="`${PREFIX}__texto`"
      placeholder="Escribe aquí tu instrucción…"
      :aria-describedby="`${PREFIX}-conteo ${PREFIX}-ayuda`"
      :readonly="ocupado"
    ></textarea>
    <p :id="`${PREFIX}-conteo`" :class="`${PREFIX}__conteo`" aria-live="polite">
      {{ piezasEscritas }} de {{ totalPiezas }} piezas
    </p>
    <template v-if="!compacto">
      <v-cargando v-if="ocupado">Evaluando tu instrucción…</v-cargando>
      <v-button v-else bloque :deshabilitado="!puedePedir" @click="$emit('pedir')">Pedir a la IA</v-button>
      <p :id="`${PREFIX}-ayuda`" :class="`${PREFIX}__ayuda`">
        {{
          puedePedir
            ? "Revisaremos qué piezas tiene tu instrucción."
            : "Escribe algo o usa la plantilla para continuar."
        }}
      </p>
    </template>
    <span v-else :id="`${PREFIX}-ayuda`" hidden></span>
  </section>
</template>

<script src="./cmp-editor-instruccion.ts" lang="ts"></script>

<style src="./cmp-editor-instruccion.scss" lang="scss" scoped></style>
