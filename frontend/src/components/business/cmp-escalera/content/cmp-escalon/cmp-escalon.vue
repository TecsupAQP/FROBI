<template>
  <li :class="[PREFIX, `${PREFIX}--${estado}`]" :aria-current="estado === 'activo' ? 'step' : undefined">
    <span :class="`${PREFIX}__marca`" aria-hidden="true">
      <v-icon v-if="estado === 'hecho'" nombre="check" :tamano="22" />
      <v-icon v-else-if="estado === 'bloqueado'" nombre="lock" :tamano="20" />
      <template v-else>{{ numero }}</template>
    </span>
    <div :class="`${PREFIX}__cuerpo`">
      <h3 :class="`${PREFIX}__titulo`">
        {{ escalon.titulo }}
        <span class="solo-lector">· {{ ESTADO_TEXTO[estado] }}</span>
      </h3>
      <template v-if="estado === 'bloqueado'">
        <p :class="`${PREFIX}__bloqueo`">{{ textoBloqueo }}</p>
      </template>
      <template v-else>
        <p v-for="linea in escalon.contenido" :key="linea" :class="`${PREFIX}__texto`">{{ linea }}</p>
      </template>
      <slot />
    </div>
  </li>
</template>

<script src="./cmp-escalon.ts" lang="ts"></script>

<style src="./cmp-escalon.scss" lang="scss" scoped></style>
