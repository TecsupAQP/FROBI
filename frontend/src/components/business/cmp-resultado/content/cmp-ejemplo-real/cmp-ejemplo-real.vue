<template>
  <div :class="PREFIX">
    <figure v-if="contenido.conIlustracion" :class="`${PREFIX}__ilustracion`">
      <figcaption class="solo-lector">
        Ilustración: tres botellas con tapa metálica avanzan por una faja; el sensor inductivo, encima de la
        botella del centro, detecta su tapa y enciende su luz verde.
      </figcaption>
      <span :class="`${PREFIX}__etiqueta ${PREFIX}__etiqueta--sensor`" aria-hidden="true"
        >Sensor inductivo</span
      >
      <span :class="`${PREFIX}__etiqueta ${PREFIX}__etiqueta--tapa`" aria-hidden="true">Tapa metálica</span>
      <span :class="`${PREFIX}__etiqueta ${PREFIX}__etiqueta--faja`" aria-hidden="true">Faja avanza →</span>

      <div :class="`${PREFIX}__sensor`" aria-hidden="true">
        <span :class="`${PREFIX}__sensor-cuerpo`"></span>
        <span :class="`${PREFIX}__sensor-cabeza`"></span>
        <img :class="`${PREFIX}__campo`" :src="imgCampo" alt="" width="96" height="44" />
        <img :class="`${PREFIX}__luz`" :src="imgLuz" alt="" width="16" height="16" />
      </div>

      <div
        v-for="posicion in POSICIONES_BOTELLA"
        :key="posicion"
        :class="[`${PREFIX}__botella`, `${PREFIX}__botella--${posicion}`]"
        aria-hidden="true"
      >
        <span :class="`${PREFIX}__tapa`"></span>
        <span :class="`${PREFIX}__cuello`"></span>
        <span :class="`${PREFIX}__cuerpo`"></span>
      </div>

      <span :class="`${PREFIX}__faja`" aria-hidden="true"></span>
      <img
        :class="`${PREFIX}__rodillo ${PREFIX}__rodillo--inicio`"
        :src="imgRodillo"
        alt=""
        width="22"
        height="22"
      />
      <img
        :class="`${PREFIX}__rodillo ${PREFIX}__rodillo--fin`"
        :src="imgRodillo"
        alt=""
        width="22"
        height="22"
      />
    </figure>

    <ol :class="`${PREFIX}__pasos`">
      <li v-for="(paso, indice) in contenido.pasos" :key="paso" :class="`${PREFIX}__paso`">
        <span :class="`${PREFIX}__numero`" aria-hidden="true">{{ indice + 1 }}</span>
        <span>{{ paso }}</span>
      </li>
    </ol>

    <v-aviso v-if="contenido.advertencia" tipo="aviso">{{ contenido.advertencia }}</v-aviso>
  </div>
</template>

<script src="./cmp-ejemplo-real.ts" lang="ts"></script>

<style src="./cmp-ejemplo-real.scss" lang="scss" scoped></style>
