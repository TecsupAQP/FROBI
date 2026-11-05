<template>
  <section :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <div :class="`${PREFIX}__encabezado`">
      <h2 :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">Mis guías</h2>
      <p :class="`${PREFIX}__secundario`">Todas las que subiste quedan guardadas. Elige con cuál estudiar.</p>
    </div>
    <ul :class="`${PREFIX}__lista`">
      <li
        v-for="guia in guias"
        :key="guia.id"
        :class="[`${PREFIX}__guia`, { [`${PREFIX}__guia--actual`]: guia.actual }]"
      >
        <span :class="`${PREFIX}__icono`" aria-hidden="true">
          <v-icon :nombre="ICONOS[guia.origen]" :tamano="24" />
        </span>
        <div :class="`${PREFIX}__textos`">
          <h3 :class="`${PREFIX}__nombre`">{{ guia.titulo }}</h3>
          <p :class="`${PREFIX}__origen`">{{ ORIGENES[guia.origen] }}</p>
          <p :class="`${PREFIX}__vista`">{{ guia.vistaPrevia }}</p>
        </div>
        <v-chip v-if="guia.actual" tono="exito" icono="check">Estás estudiando esta</v-chip>
        <v-button
          v-else
          variante="secundario"
          :deshabilitado="eligiendo !== null"
          :etiqueta="`Estudiar ${guia.titulo}`"
          @click="$emit('elegir', guia.id)"
        >
          {{ eligiendo === guia.id ? "Abriendo…" : "Estudiar esta" }}
        </v-button>
      </li>
    </ul>
  </section>
</template>

<script src="./cmp-mis-guias.ts" lang="ts"></script>

<style src="./cmp-mis-guias.scss" lang="scss" scoped></style>
