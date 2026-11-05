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

    <v-aviso v-if="vieneSinGuia && sinGuia" tipo="aviso" icono="info">
      Para estudiar, primero sube tu guía o pega su texto.
    </v-aviso>

    <div :class="`${PREFIX}__columnas`">
      <cmp-tarjeta-guia v-if="guia" data-recorrido="guia-actual" :class="`${PREFIX}__guia`" :guia="guia" />
      <v-estado-vacio
        v-else-if="sinGuia"
        data-recorrido="guia-actual"
        :class="`${PREFIX}__guia`"
        icono="upload"
        titulo="Empieza con tu guía"
        texto="Sube el PDF de tu curso o pega su texto. FROBI lo adapta a tu manera de aprender."
      >
        <v-button icono="upload" @click="abrirModal">Subir mi PDF</v-button>
        <v-button
          v-if="guiaEjemplo"
          variante="texto"
          :deshabilitado="eligiendo !== null"
          @click="estudiar(guiaEjemplo.id)"
        >
          Solo quiero probar con una guía de ejemplo
        </v-button>
      </v-estado-vacio>
      <div v-else :class="`${PREFIX}__guia ${PREFIX}__cargando`">
        <v-cargando>Cargando tus guías…</v-cargando>
      </div>
      <!-- Sin guía, el estado vacío ya invita a subirla: no se repite la tarjeta. -->
      <cmp-tarjeta-subir
        v-if="!sinGuia"
        data-recorrido="subir-guia"
        :class="`${PREFIX}__subir`"
        @subir="abrirModal"
      />
    </div>

    <cmp-mis-guias
      v-if="guiasClase.length"
      data-recorrido="material-clase"
      prefijo-id="material-clase"
      :titulo="nombreClase ? `Material de tu clase · ${nombreClase}` : 'Material de tu clase'"
      descripcion="Lo sube tu docente. Elige con cuál estudiar; lo verás en el formato que prefieras."
      :guias="guiasClase"
      :eligiendo="eligiendo"
      @elegir="estudiar"
    />

    <cmp-mis-guias v-if="propias.length > 1" :guias="propias" :eligiendo="eligiendo" @elegir="estudiar" />

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
