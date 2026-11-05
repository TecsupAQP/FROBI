<template>
  <section :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <div :class="`${PREFIX}__encabezado`">
      <h2 :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">Tu autonomía</h2>
      <p :class="`${PREFIX}__nivel`">Nivel {{ autonomia.nivelActual }} de {{ autonomia.niveles.length }}</p>
    </div>
    <ol :class="`${PREFIX}__niveles`">
      <li
        v-for="nivel in autonomia.niveles"
        :key="nivel.nivel"
        :class="[`${PREFIX}__item`, `${PREFIX}__item--${nivel.estado}`]"
        :aria-current="nivel.estado === 'actual' ? 'step' : undefined"
      >
        <span :class="`${PREFIX}__marca`" aria-hidden="true">
          <v-icon v-if="nivel.estado === 'superado'" nombre="check" :tamano="18" />
          <v-icon v-else-if="nivel.estado === 'bloqueado'" nombre="lock" :tamano="18" />
          <template v-else>{{ nivel.nivel }}</template>
        </span>
        <span :class="`${PREFIX}__textos`">
          <span :class="`${PREFIX}__nombre`">Nivel {{ nivel.nivel }}</span>
          <span :class="`${PREFIX}__detalle`">{{ nivel.nombre }}{{ SUFIJOS[nivel.estado] }}</span>
        </span>
      </li>
    </ol>
    <p :class="`${PREFIX}__mensaje`">{{ autonomia.mensaje }}</p>
  </section>
</template>

<script src="./cmp-autonomia.ts" lang="ts"></script>

<style src="./cmp-autonomia.scss" lang="scss" scoped></style>
