<template>
  <div :class="PREFIX">
    <header :class="`${PREFIX}__encabezado`">
      <div :class="`${PREFIX}__titulos`">
        <p v-if="ruta.length" :class="`${PREFIX}__ruta`">{{ ruta.join(" › ") }}</p>
        <h1 :class="`${PREFIX}__titulo`">{{ titulo }}</h1>
      </div>
      <v-button :class="`${PREFIX}__pidelo`" :destino="{ name: RutaEnum.PIDELO_TU }">Pídelo tú</v-button>
    </header>

    <section v-if="adaptacion?.esRespaldo && !estaCargando" :class="`${PREFIX}__respaldo`" role="status">
      <span :class="`${PREFIX}__respaldo-icono`" aria-hidden="true">
        <v-icon nombre="save" />
      </span>
      <div :class="`${PREFIX}__respaldo-textos`">
        <h2 :class="`${PREFIX}__respaldo-titulo`">Mostramos una versión guardada de esta guía</h2>
        <p>
          {{
            adaptacion.aviso ||
            "La IA no respondió a tiempo. Puedes seguir estudiando con esta versión o intentar de nuevo."
          }}
        </p>
      </div>
      <v-button variante="secundario" @click="cargarAdaptacion(temaId, formato, true)"
        >Reintentar con la IA</v-button
      >
    </section>

    <cmp-selector-formato :activo="formatoActual" />

    <v-aviso v-if="estado === EstadoCargaEnum.SIN_CONEXION" tipo="error">
      Sin conexión. Revisa tu internet y vuelve a intentarlo.
      <v-button variante="texto" @click="$emit('reintentar')">Reintentar</v-button>
    </v-aviso>

    <div v-else :class="`${PREFIX}__columnas`">
      <div :class="`${PREFIX}__principal`" aria-live="polite" :aria-busy="estaCargando">
        <div v-if="estaCargando || !adaptacion" :class="`${PREFIX}__cargando`">
          <v-cargando>Adaptando a {{ definicionFormato.nombre.toLowerCase() }}…</v-cargando>
        </div>
        <template v-else>
          <cmp-tarjeta-resultado :formato="definicionFormato" :tema="adaptacion.titulo">
            <cmp-mapa-visual v-if="contenido?.formato === 'mapa-visual'" :contenido="contenido" />
            <cmp-ejemplo-real v-else-if="contenido?.formato === 'ejemplo-real'" :contenido="contenido" />
            <cmp-lectura-facil v-else-if="contenido?.formato === 'lectura-facil'" :contenido="contenido" />
            <cmp-audio
              v-else-if="contenido?.formato === 'audio'"
              :key="adaptacion.temaId"
              :contenido="contenido"
            />
          </cmp-tarjeta-resultado>
        </template>
      </div>

      <aside v-if="receta.length" :class="`${PREFIX}__lateral`" aria-label="Cómo se pidió este resultado">
        <cmp-receta-ia
          data-recorrido="receta"
          :receta="receta"
          :desplegada="recetaDesplegada"
          @alternar="alternarReceta"
          @copiar="copiarReceta"
        />
        <v-aviso tipo="nota">La IA puede equivocarse; contrasta con tu guía.</v-aviso>
      </aside>
    </div>
  </div>
</template>

<script src="./cmp-resultado.ts" lang="ts"></script>

<style src="./cmp-resultado.scss" lang="scss" scoped></style>
