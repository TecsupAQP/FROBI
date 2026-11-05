<template>
  <div :class="PREFIX">
    <div v-if="!resumen" :class="`${PREFIX}__cargando`">
      <v-cargando>Preparando tu resumen…</v-cargando>
    </div>

    <template v-else>
      <header :class="`${PREFIX}__encabezado`">
        <span :class="`${PREFIX}__logro`" aria-hidden="true">
          <v-icon nombre="check" :tamano="38" />
        </span>
        <div>
          <h1 :class="`${PREFIX}__titulo`">¡Terminaste el recorrido!</h1>
          <p :class="`${PREFIX}__subtitulo`">Resumen del tema «{{ resumen.tema }}»</p>
        </div>
      </header>

      <div :class="`${PREFIX}__columnas`">
        <section :class="`${PREFIX}__receta`" aria-labelledby="cierre-receta">
          <div>
            <h2 id="cierre-receta" :class="`${PREFIX}__seccion-titulo`">La receta que aprendiste</h2>
            <p :class="`${PREFIX}__secundario`">Cuatro piezas que puedes usar con cualquier tema.</p>
          </div>
          <ul :class="`${PREFIX}__piezas`">
            <li v-for="pieza in resumen.receta" :key="pieza.pieza">
              <v-tarjeta-pieza :pieza="pieza.pieza">{{ pieza.texto }}</v-tarjeta-pieza>
            </li>
          </ul>
          <v-button variante="secundario" @click="copiarReceta">Copiar receta</v-button>
        </section>

        <div :class="`${PREFIX}__lateral`">
          <section :class="`${PREFIX}__dato`">
            <div :class="`${PREFIX}__dato-cabecera`">
              <span :class="`${PREFIX}__dato-icono`" aria-hidden="true"
                ><v-icon nombre="bulb" :tamano="26"
              /></span>
              <div>
                <h2 :class="`${PREFIX}__dato-etiqueta`">Formato usado</h2>
                <p :class="`${PREFIX}__dato-valor`">{{ nombreFormato }}</p>
              </div>
            </div>
          </section>

          <section :class="`${PREFIX}__dato`">
            <div :class="`${PREFIX}__dato-cabecera`">
              <span :class="`${PREFIX}__dato-icono`" aria-hidden="true"
                ><v-icon nombre="star" :tamano="26"
              /></span>
              <div>
                <h2 :class="`${PREFIX}__dato-etiqueta`">Puntaje de tu instrucción</h2>
                <p :class="`${PREFIX}__dato-valor`">
                  {{ resumen.piezasLogradas.length }} de {{ resumen.totalPiezas }} piezas
                </p>
              </div>
            </div>
            <ul :class="`${PREFIX}__chips`" aria-label="Piezas logradas">
              <li v-for="pieza in resumen.piezasLogradas" :key="pieza">
                <v-chip-pieza :class="`${PREFIX}__chip`" :pieza="pieza" compacto>
                  <v-icon nombre="check" :tamano="16" />
                  {{ nombrePieza(pieza) }}
                </v-chip-pieza>
              </li>
            </ul>
          </section>

          <section :class="`${PREFIX}__dato`">
            <div :class="`${PREFIX}__dato-cabecera`">
              <span :class="`${PREFIX}__dato-icono`" aria-hidden="true"
                ><v-icon nombre="gauge" :tamano="26"
              /></span>
              <div>
                <h2 :class="`${PREFIX}__dato-etiqueta`">Autonomía alcanzada</h2>
                <p :class="`${PREFIX}__dato-valor`">
                  Nivel {{ resumen.autonomia.nivel }} · {{ resumen.autonomia.nombre }}
                </p>
              </div>
            </div>
            <div
              :class="`${PREFIX}__niveles`"
              role="img"
              :aria-label="`Nivel ${resumen.autonomia.nivel} de ${resumen.autonomia.total}`"
            >
              <span
                v-for="nivel in resumen.autonomia.total"
                :key="nivel"
                :class="[
                  `${PREFIX}__nivel`,
                  { [`${PREFIX}__nivel--logrado`]: nivel <= resumen.autonomia.nivel },
                ]"
              ></span>
            </div>
            <p :class="`${PREFIX}__secundario`">{{ resumen.autonomia.mensaje }}</p>
          </section>
        </div>
      </div>

      <div :class="`${PREFIX}__acciones`">
        <v-button :destino="{ name: RutaEnum.GUIA }">Aprender otro tema</v-button>
        <v-button variante="secundario" :destino="{ name: RutaEnum.PROGRESO }">Ver mi progreso</v-button>
      </div>
    </template>
  </div>
</template>

<script src="./cmp-cierre.ts" lang="ts"></script>

<style src="./cmp-cierre.scss" lang="scss" scoped></style>
