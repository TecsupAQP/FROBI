<template>
  <div :class="PREFIX">
    <header :class="`${PREFIX}__encabezado`">
      <h1 :class="`${PREFIX}__titulo`">Cómo se usa FROBI: de la clase al avance</h1>
      <p :class="`${PREFIX}__descripcion`">
        Una docente invita a 2 alumnos. Ellos aprenden con ayudas y también practican sin IA. Ella ve su
        avance. Nombres y datos de ejemplo.
      </p>
    </header>

    <div :class="`${PREFIX}__leyenda`">
      <v-chip tono="marino">Docente</v-chip>
      <v-chip tono="marca">Estudiante</v-chip>
      <span :class="`${PREFIX}__leyenda-texto`"
        >Cada pantalla del recorrido lleva una etiqueta «Paso n» arriba.</span
      >
    </div>

    <ol :class="`${PREFIX}__pasos`">
      <li v-for="paso in RECORRIDO_MOCK" :key="paso.numero" :class="`${PREFIX}__paso`">
        <v-chip :tono="paso.quien === 'estudiante' ? 'marca' : 'marino'" :class="`${PREFIX}__chip`">
          Paso {{ paso.numero }} · {{ paso.etiqueta }}
        </v-chip>
        <h2 :class="`${PREFIX}__paso-titulo`">{{ paso.titulo }}</h2>
        <p :class="`${PREFIX}__paso-texto`">{{ paso.texto }}</p>
        <router-link :class="`${PREFIX}__enlace`" :to="paso.destino">
          <v-icon nombre="arrow" :tamano="20" />
          {{ paso.enlace }}
        </router-link>
      </li>
    </ol>
  </div>
</template>

<script src="./cmp-como-se-usa.ts" lang="ts"></script>

<style src="./cmp-como-se-usa.scss" lang="scss" scoped></style>
