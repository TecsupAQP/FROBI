<template>
  <li :class="[PREFIX, `${PREFIX}--${linea.quien}`, `${PREFIX}--${linea.estado}`]">
    <span v-if="linea.quien === 'frobi'" :class="`${PREFIX}__avatar`" aria-hidden="true">
      <img :src="logoIcono" alt="" width="22" height="22" />
    </span>
    <div :class="`${PREFIX}__cuerpo`">
      <span class="solo-lector">{{ linea.quien === "frobi" ? "FROBI dice:" : "Tú preguntaste:" }}</span>
      <p :class="`${PREFIX}__burbuja`" :aria-busy="linea.estado === 'escribiendo' || undefined">
        {{ linea.texto
        }}<span v-if="linea.estado === 'escribiendo'" :class="`${PREFIX}__cursor`" aria-hidden="true"></span>
      </p>
      <span v-if="linea.estado === 'respaldo'" :class="`${PREFIX}__nota`">
        <v-icon nombre="info" :tamano="16" />
        Respuesta sin IA
      </span>
      <span v-else-if="linea.estado === 'pendiente'" :class="`${PREFIX}__nota`">Enviando…</span>
    </div>
  </li>
</template>

<script src="./cmp-mensaje-chat.ts" lang="ts"></script>

<style src="./cmp-mensaje-chat.scss" lang="scss" scoped></style>
