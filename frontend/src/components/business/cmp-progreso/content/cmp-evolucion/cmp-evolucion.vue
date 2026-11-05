<template>
  <section :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <div>
      <h2 :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">Evolución de tus instrucciones</h2>
      <p :class="`${PREFIX}__subtitulo`">Piezas completas en cada intento (de {{ maximo }})</p>
    </div>
    <figure :class="`${PREFIX}__grafico`">
      <div :class="`${PREFIX}__lienzo`" aria-hidden="true">
        <span
          v-for="guia in GUIAS"
          :key="guia"
          :class="`${PREFIX}__guia`"
          :style="{ top: `${guia}px` }"
        ></span>
        <svg
          :class="`${PREFIX}__linea`"
          :viewBox="`0 0 ${intentos.length * 100} ${ALTO}`"
          preserveAspectRatio="none"
        >
          <polyline
            :points="puntosSvg"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            vector-effect="non-scaling-stroke"
          />
        </svg>
        <span
          v-for="(punto, indice) in puntos"
          :key="indice"
          :class="`${PREFIX}__punto`"
          :style="{ left: `${punto.xPorcentaje}%`, top: `${punto.y}px` }"
        ></span>
      </div>
      <figcaption>
        <ol :class="`${PREFIX}__intentos`">
          <li v-for="(valor, indice) in intentos" :key="indice" :class="`${PREFIX}__intento`">
            <span :class="`${PREFIX}__intento-nombre`">Intento {{ indice + 1 }}</span>
            <span
              :class="[
                `${PREFIX}__intento-valor`,
                { [`${PREFIX}__intento-valor--completo`]: valor === maximo },
              ]"
            >
              {{ valor }}/{{ maximo }}
            </span>
          </li>
        </ol>
      </figcaption>
    </figure>
  </section>
</template>

<script src="./cmp-evolucion.ts" lang="ts"></script>

<style src="./cmp-evolucion.scss" lang="scss" scoped></style>
