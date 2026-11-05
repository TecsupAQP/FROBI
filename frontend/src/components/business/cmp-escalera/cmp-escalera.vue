<template>
  <div :class="PREFIX">
    <div v-if="!tarea" :class="`${PREFIX}__cargando`">
      <v-cargando>Preparando las pistas…</v-cargando>
    </div>

    <template v-else>
      <v-chip tono="marca">Paso 6 · Estudiante</v-chip>
      <cmp-encabezado-pagina :titulo="tarea.titulo" :descripcion="tarea.ruta.join(' · ')" />

      <div :class="`${PREFIX}__columnas`">
        <section :class="`${PREFIX}__escalera`" aria-labelledby="escalera-titulo">
          <h2 id="escalera-titulo" :class="`${PREFIX}__titulo`">Escalera de ayuda</h2>
          <ol :class="`${PREFIX}__escalones`">
            <cmp-escalon
              v-for="(escalon, indice) in escalonesVisibles"
              :key="escalon.id"
              :escalon="escalon"
              :numero="indice + 1"
              :estado="estadoDe(escalon.id)"
              :texto-bloqueo="BLOQUEOS[escalon.id]"
            >
              <form
                v-if="escalon.id === 'pista-2' && !progreso.resultado"
                :class="`${PREFIX}__intento`"
                @submit.prevent="probarIntento"
              >
                <v-field
                  id="escalera-intento"
                  :model-value="progreso.intento"
                  etiqueta="Tu intento"
                  placeholder="Creo que es el capacitivo porque…"
                  @update:model-value="escribirIntento"
                />
                <v-cargando v-if="probando">Revisando tu intento…</v-cargando>
                <v-button v-else tipo="submit" bloque :deshabilitado="!progreso.intento.trim()">
                  Probar mi respuesta
                </v-button>
              </form>
              <div
                v-if="escalon.id === 'respuesta' && progreso.resultado"
                :class="[
                  `${PREFIX}__resultado`,
                  progreso.resultado.correcto
                    ? `${PREFIX}__resultado--bien`
                    : `${PREFIX}__resultado--revisar`,
                ]"
                role="status"
              >
                <v-icon :nombre="progreso.resultado.correcto ? 'check' : 'info'" :tamano="20" />
                <span>{{ progreso.resultado.comentario }}</span>
              </div>
            </cmp-escalon>
          </ol>
          <p v-if="escalonesOcultos" :class="`${PREFIX}__nota`">
            <v-icon nombre="type" :tamano="20" />
            Textos cortos: verás el siguiente escalón cuando avances.
          </p>
        </section>

        <aside :class="`${PREFIX}__lateral`" aria-labelledby="escalera-decides">
          <h2 id="escalera-decides" :class="`${PREFIX}__titulo`">Tú decides cuánta ayuda usar</h2>
          <v-chip icono="info">Nivel 2 · con pistas</v-chip>
          <p :class="`${PREFIX}__texto`">
            FROBI no te da la respuesta de golpe: te guía por pasos y la respuesta llega al final.
          </p>
          <v-button
            variante="secundario"
            bloque
            :deshabilitado="progreso.pasoAPasoAbierto"
            @click="abrirPasoAPaso"
          >
            {{ progreso.pasoAPasoAbierto ? "Paso a paso abierto" : "Necesito el paso a paso" }}
          </v-button>
          <v-button
            variante="secundario"
            bloque
            :destino="{ name: RutaEnum.SIN_IA, params: { tarea: tarea.id } }"
          >
            Intentarlo sin IA
          </v-button>
        </aside>
      </div>
    </template>
  </div>
</template>

<script src="./cmp-escalera.ts" lang="ts"></script>

<style src="./cmp-escalera.scss" lang="scss" scoped></style>
