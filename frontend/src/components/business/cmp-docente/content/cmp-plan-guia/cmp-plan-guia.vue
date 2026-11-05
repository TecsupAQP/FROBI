<template>
  <div :class="PREFIX">
    <fieldset :class="`${PREFIX}__modos`">
      <legend :class="`${PREFIX}__leyenda`">¿Cómo se trabaja esta guía?</legend>
      <v-radio-opcion
        :nombre="`${prefijoId}-modo`"
        valor="estudio"
        :model-value="modoElegido"
        @update:model-value="elegirModo"
      >
        <span :class="`${PREFIX}__opcion`">Guía de estudio</span>
        <span :class="`${PREFIX}__detalle`">Sin tareas. Al final, la IA le hace preguntas al alumno.</span>
      </v-radio-opcion>
      <v-radio-opcion
        :nombre="`${prefijoId}-modo`"
        valor="tareas"
        :model-value="modoElegido"
        @update:model-value="elegirModo"
      >
        <span :class="`${PREFIX}__opcion`">Guía con tareas</span>
        <span :class="`${PREFIX}__detalle`">Tú escribes los ejercicios que el alumno debe resolver.</span>
      </v-radio-opcion>
    </fieldset>

    <div v-if="modoElegido === 'tareas'" :class="`${PREFIX}__tareas`">
      <div v-for="(tarea, indice) in lista" :key="indice" :class="`${PREFIX}__tarea`">
        <v-field
          :id="`${prefijoId}-tarea-${indice}`"
          :class="`${PREFIX}__campo`"
          :etiqueta="`Tarea ${indice + 1}`"
          placeholder="Ej.: Explica con tus palabras cómo funciona un motor de inducción."
          multilinea
          :filas="2"
          :model-value="tarea"
          @update:model-value="escribir(indice, $event)"
        />
        <v-button
          v-if="lista.length > 1"
          variante="texto"
          icono="x"
          :etiqueta="`Quitar la tarea ${indice + 1}`"
          @click="quitar(indice)"
        >
          Quitar
        </v-button>
      </div>
      <v-button
        v-if="lista.length < MAX_TAREAS"
        variante="texto"
        icono="pencil"
        :class="`${PREFIX}__agregar`"
        @click="agregar"
      >
        Agregar otra tarea
      </v-button>
    </div>
  </div>
</template>

<script src="./cmp-plan-guia.ts" lang="ts"></script>

<style src="./cmp-plan-guia.scss" lang="scss" scoped></style>
