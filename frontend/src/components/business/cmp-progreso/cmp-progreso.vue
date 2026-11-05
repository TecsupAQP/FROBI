<template>
  <div :class="PREFIX">
    <div
      v-if="estado === EstadoCargaEnum.CARGANDO || estado === EstadoCargaEnum.INICIAL"
      :class="`${PREFIX}__cargando`"
    >
      <v-cargando>Cargando tu progreso…</v-cargando>
    </div>

    <v-estado-vacio
      v-else-if="!progreso"
      icono="chart"
      titulo="Aún no tienes progreso"
      texto="Responde una pregunta de verificación y verás aquí tus aciertos por formato."
    >
      <v-button :destino="{ name: RutaEnum.GUIA }">Ir a la guía</v-button>
    </v-estado-vacio>

    <template v-else>
      <cmp-encabezado-pagina
        titulo="Mi progreso"
        :descripcion="`Alias: ${progreso.alias} · Guía: ${progreso.guia}`"
      />

      <section :class="`${PREFIX}__mensaje`" :aria-labelledby="`${PREFIX}-mensaje`">
        <span :class="`${PREFIX}__mensaje-icono`" aria-hidden="true">
          <v-icon nombre="bulb" :tamano="30" />
        </span>
        <div>
          <h2 :id="`${PREFIX}-mensaje`" :class="`${PREFIX}__mensaje-titulo`">
            {{ progreso.mensaje.titulo }}
          </h2>
          <p>{{ progreso.mensaje.texto }}</p>
        </div>
      </section>

      <dl :class="`${PREFIX}__datos`">
        <div :class="`${PREFIX}__dato`">
          <dt>Temas practicados</dt>
          <dd>{{ progreso.temasPracticados }}</dd>
        </div>
        <div :class="`${PREFIX}__dato`">
          <dt>Mejor formato</dt>
          <dd>{{ nombreFormato(progreso.mejorFormato) }}</dd>
        </div>
        <div :class="`${PREFIX}__dato`">
          <dt>Autonomía</dt>
          <dd>{{ progreso.autonomia }}</dd>
        </div>
      </dl>

      <div :class="`${PREFIX}__columnas`">
        <section :class="`${PREFIX}__aciertos`" :aria-labelledby="`${PREFIX}-aciertos`">
          <div>
            <h2 :id="`${PREFIX}-aciertos`" :class="`${PREFIX}__subtitulo`">Aciertos por formato</h2>
            <p :class="`${PREFIX}__secundario`">Porcentaje de preguntas acertadas</p>
          </div>
          <ul :class="`${PREFIX}__barras`">
            <li v-for="item in progreso.aciertos" :key="item.formato" :class="`${PREFIX}__barra-item`">
              <span :class="`${PREFIX}__barra-fila`">
                <span>{{ nombreFormato(item.formato) }}</span>
                <span :class="`${PREFIX}__barra-valor`">{{ item.porcentaje }} %</span>
              </span>
              <span
                :class="[
                  `${PREFIX}__barra`,
                  { [`${PREFIX}__barra--mejor`]: item.formato === progreso.mejorFormato },
                ]"
                role="img"
                :aria-label="`${nombreFormato(item.formato)}: ${item.porcentaje} % de aciertos`"
              >
                <span :class="`${PREFIX}__barra-relleno`" :style="{ width: `${item.porcentaje}%` }"></span>
              </span>
            </li>
          </ul>
        </section>
        <cmp-evolucion :class="`${PREFIX}__evolucion`" :intentos="progreso.intentos" />
      </div>
    </template>
  </div>
</template>

<script src="./cmp-progreso.ts" lang="ts"></script>

<style src="./cmp-progreso.scss" lang="scss" scoped></style>
