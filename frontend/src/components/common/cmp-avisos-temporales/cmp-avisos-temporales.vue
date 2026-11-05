<template>
  <div :class="PREFIX" role="status" aria-live="polite">
    <transition-group :name="PREFIX">
      <div v-for="aviso in avisos" :key="aviso.id" :class="`${PREFIX}__aviso`">
        <span :class="`${PREFIX}__icono`" aria-hidden="true"><v-icon nombre="check" :tamano="16" /></span>
        <span :class="`${PREFIX}__textos`">
          <span :class="`${PREFIX}__titulo`">{{ aviso.titulo }}</span>
          <span v-if="aviso.detalle" :class="`${PREFIX}__detalle`">{{ aviso.detalle }}</span>
        </span>
        <button
          type="button"
          :class="`${PREFIX}__cerrar`"
          aria-label="Cerrar aviso"
          @click="quitarAviso(aviso.id)"
        >
          <v-icon nombre="x" :tamano="20" />
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script src="./cmp-avisos-temporales.ts" lang="ts"></script>

<style src="./cmp-avisos-temporales.scss" lang="scss" scoped></style>
