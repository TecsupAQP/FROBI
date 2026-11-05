<template>
  <div :class="PREFIX">
    <header :class="`${PREFIX}__saludo`">
      <h1 :class="`${PREFIX}__titulo`">Hola, {{ alias }}</h1>
      <p :class="`${PREFIX}__subtitulo`">
        ¿Qué quieres aprender hoy?<span :class="`${PREFIX}__extra`">
          Elige una guía y la adaptamos para ti.</span
        >
      </p>
    </header>

    <div :class="`${PREFIX}__columnas`">
      <cmp-tarjeta-guia v-if="guia" :class="`${PREFIX}__guia`" :guia="guia" />
      <div v-else :class="`${PREFIX}__guia ${PREFIX}__cargando`">
        <v-cargando>Cargando tus guías…</v-cargando>
      </div>
      <cmp-tarjeta-subir :class="`${PREFIX}__subir`" @subir="abrirModal" />
    </div>

    <cmp-mis-guias v-if="guias.length > 1" :guias="guias" :eligiendo="eligiendo" @elegir="estudiar" />

    <cmp-subir-pdf
      v-model="modalAbierto"
      :fase="fase"
      :progreso="progreso"
      :nombre-archivo="nombreArchivo"
      :tamano-archivo-mb="tamanoArchivoMb"
      :archivo="archivo"
      @elegir="elegirArchivo"
      @cancelar="cancelarSubida"
      @usar="usarGuia"
    />
  </div>
</template>

<script src="./cmp-inicio.ts" lang="ts"></script>

<style src="./cmp-inicio.scss" lang="scss" scoped></style>
