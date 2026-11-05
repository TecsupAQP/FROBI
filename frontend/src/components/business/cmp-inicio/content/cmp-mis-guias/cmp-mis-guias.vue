<template>
  <section :class="PREFIX" :aria-labelledby="`${prefijoId}-titulo`">
    <div :class="`${PREFIX}__encabezado`">
      <h2 :id="`${prefijoId}-titulo`" :class="`${PREFIX}__titulo`">{{ titulo }}</h2>
      <p :class="`${PREFIX}__secundario`">{{ descripcion }}</p>
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
          <div v-if="guia.enClase" :class="`${PREFIX}__clase`">
            <div :class="`${PREFIX}__avance`">
              <v-progress-bar
                :class="`${PREFIX}__barra`"
                :valor="guia.enClase.avance"
                :etiqueta="`Avance en ${guia.titulo}`"
                :texto-valor="resumenAvance(guia.enClase)"
                :tono="guia.enClase.avance === 100 ? 'exito' : 'marca'"
              />
              <span :class="`${PREFIX}__porcentaje`">{{ guia.enClase.avance }} %</span>
            </div>
            <p :class="`${PREFIX}__secundario`">{{ resumenAvance(guia.enClase) }}</p>
            <ol v-if="guia.enClase.modo === 'tareas'" :class="`${PREFIX}__tareas`">
              <li v-for="tarea in guia.enClase.tareas" :key="tarea.ref" :class="`${PREFIX}__tarea`">
                <v-icon
                  :class="`${PREFIX}__marca`"
                  :nombre="tarea.hecha ? 'check-circle' : 'clock'"
                  :tamano="20"
                  :etiqueta="tarea.hecha ? 'Hecha' : 'Pendiente'"
                />
                <span :class="`${PREFIX}__enunciado`">{{ tarea.enunciado }}</span>
                <v-button
                  variante="texto"
                  icono-fin="arrow"
                  :deshabilitado="eligiendo !== null"
                  :etiqueta="`${tarea.hecha ? 'Repasar' : 'Resolver'} la tarea ${tarea.numero}`"
                  @click="$emit('resolver', guia.id, tarea.ref)"
                >
                  {{ tarea.hecha ? "Repasar" : "Resolver" }}
                </v-button>
              </li>
            </ol>
            <v-button
              v-else
              variante="secundario"
              icono="check"
              :class="`${PREFIX}__evaluar`"
              :deshabilitado="eligiendo !== null"
              :etiqueta="`Evaluación final de ${guia.titulo}`"
              @click="$emit('evaluar', guia.id)"
            >
              {{ guia.enClase.evaluacion ? "Repetir la evaluación final" : "Hacer la evaluación final" }}
            </v-button>
          </div>
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
