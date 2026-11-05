<template>
  <div :class="PREFIX">
    <cmp-encabezado-pagina
      titulo="Verifica lo que aprendiste"
      :antetitulo="verificacion ? verificacion.ruta.join(' › ') : undefined"
    />

    <div v-if="!pregunta" :class="`${PREFIX}__cargando`">
      <v-cargando>Preparando preguntas…</v-cargando>
    </div>

    <template v-else>
      <div :class="`${PREFIX}__progreso`">
        <p :class="`${PREFIX}__progreso-texto`">Pregunta {{ indice + 1 }} de {{ total }}</p>
        <div
          :class="`${PREFIX}__barras`"
          role="progressbar"
          :aria-valuenow="indice + 1"
          aria-valuemin="1"
          :aria-valuemax="total"
          aria-label="Avance de la verificación"
        >
          <span
            v-for="numero in total"
            :key="numero"
            :class="[`${PREFIX}__barra`, { [`${PREFIX}__barra--hecha`]: numero <= indice + 1 }]"
          ></span>
        </div>
      </div>

      <cmp-pregunta
        :key="pregunta.id"
        :pregunta="pregunta"
        :elegida="elegida"
        :revisando="revisando"
        :acerto="acerto"
        @responder="responder"
      >
        <v-button v-if="acerto" variante="secundario" @click="avanzar">
          {{ esUltima ? "Terminar" : "Siguiente pregunta" }}
        </v-button>
      </cmp-pregunta>

      <section
        v-if="elegida !== null && !acerto"
        :class="`${PREFIX}__sugerencia`"
        :aria-labelledby="`${PREFIX}-sugerencia`"
      >
        <div :class="`${PREFIX}__sugerencia-cabecera`">
          <span :class="`${PREFIX}__sugerencia-icono`" aria-hidden="true">
            <v-icon :nombre="formatoSugerido.icono" :tamano="26" />
          </span>
          <div>
            <h2 :id="`${PREFIX}-sugerencia`" :class="`${PREFIX}__sugerencia-titulo`">
              Prueba con {{ formatoSugerido.nombre }}
            </h2>
            <p>{{ formatoSugerido.descripcion }}.</p>
          </div>
        </div>
        <router-link
          :class="`${PREFIX}__sugerencia-enlace`"
          :to="{ name: RutaEnum.RESULTADO, params: { formato: formatoSugerido.id } }"
        >
          Ver en {{ formatoSugerido.nombre }}
          <v-icon nombre="arrow" :tamano="20" />
        </router-link>
      </section>

      <div v-if="elegida !== null && !acerto" :class="`${PREFIX}__acciones`">
        <v-button variante="secundario" @click="reintentar">Intentar de nuevo</v-button>
        <v-button :destino="{ name: RutaEnum.PIDELO_TU }">Pídelo tú</v-button>
      </div>

      <section v-if="acerto" :class="`${PREFIX}__siguiente`" :aria-labelledby="`${PREFIX}-siguiente`">
        <div>
          <p :class="`${PREFIX}__siguiente-antetitulo`">
            <v-icon nombre="star" :tamano="22" />
            Listo para el siguiente paso
          </p>
          <h2 :id="`${PREFIX}-siguiente`" :class="`${PREFIX}__siguiente-titulo`">Ahora hazlo a tu manera</h2>
          <p>Escribe tú la instrucción y compárala con la receta de la IA.</p>
        </div>
        <router-link :class="`${PREFIX}__siguiente-boton`" :to="{ name: RutaEnum.PIDELO_TU }">
          <v-icon nombre="pencil" :tamano="22" />
          Pídelo tú
        </router-link>
      </section>

      <v-aviso tipo="nota">La IA puede equivocarse; contrasta con tu guía.</v-aviso>
    </template>
  </div>
</template>

<script src="./cmp-verificacion.ts" lang="ts"></script>

<style src="./cmp-verificacion.scss" lang="scss" scoped></style>
