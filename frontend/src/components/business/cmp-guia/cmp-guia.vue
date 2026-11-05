<template>
  <div :class="PREFIX">
    <cmp-encabezado-pagina
      v-if="guia"
      :titulo="guia.titulo"
      :descripcion="guia.tieneArchivo ? `Guía de ${guia.carrera} · PDF` : `Guía de ${guia.carrera}`"
    />

    <div v-if="!guia" :class="`${PREFIX}__cargando`">
      <v-cargando>Cargando la guía…</v-cargando>
    </div>

    <!-- Si la guía es un PDF, se ve tal como se subió; el resto del material se estudia en los formatos. -->
    <div v-if="guia" :class="`${PREFIX}__columnas`">
      <cmp-documento-original
        v-if="guia.tieneArchivo"
        data-recorrido="documento"
        :class="`${PREFIX}__documento`"
        :titulo="guia.titulo"
        :abierto="documentoAbierto"
        :url="documentoUrl"
        :error="documentoError"
        @alternar="alternarDocumento"
      />

      <section
        data-recorrido="formatos"
        :class="`${PREFIX}__formatos`"
        :aria-labelledby="`${PREFIX}-formatos`"
      >
        <h2 :id="`${PREFIX}-formatos`" :class="`${PREFIX}__subtitulo`">¿Cómo quieres aprender este tema?</h2>
        <ul :class="`${PREFIX}__lista`">
          <li v-for="formato in FORMATOS" :key="formato.id">
            <v-card-formato
              :formato="formato"
              :elegida="formatoAdaptando === formato.id"
              :atenuada="formatoAdaptando !== null && formatoAdaptando !== formato.id"
              @elegir="elegirFormato"
            />
          </li>
        </ul>
        <div v-if="formatoAdaptando" :class="`${PREFIX}__adaptando`">
          <v-cargando>
            <span :class="`${PREFIX}__adaptando-titulo`">
              {{ tardaMucho ? "Usando una respuesta de ejemplo" : "Adaptando tu guía…" }}
            </span>
            <span :class="`${PREFIX}__adaptando-detalle`">
              {{ guia.titulo }} · {{ nombreFormato(formatoAdaptando) }}. Tarda menos de 15 segundos.
            </span>
          </v-cargando>
        </div>
        <p v-else :class="`${PREFIX}__nota`">
          Puedes cambiar de formato cuando quieras, sin volver a cargar la guía.
        </p>
      </section>
    </div>
  </div>
</template>

<script src="./cmp-guia.ts" lang="ts"></script>

<style src="./cmp-guia.scss" lang="scss" scoped></style>
