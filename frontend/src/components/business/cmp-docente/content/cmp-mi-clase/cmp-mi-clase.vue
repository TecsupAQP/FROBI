<template>
  <section :class="PREFIX" aria-labelledby="mi-clase-titulo">
    <h2 id="mi-clase-titulo" :class="`${PREFIX}__titulo`">Mi clase · {{ clase.nombre }}</h2>
    <div :class="`${PREFIX}__chips`">
      <v-chip icono="info">Código {{ clase.codigo }}</v-chip>
      <v-chip tono="exito" icono="check">{{ clase.alumnos.length }} alumnos</v-chip>
    </div>
    <ul :class="`${PREFIX}__alumnos`">
      <li v-for="alumno in clase.alumnos" :key="alumno.alias" :class="`${PREFIX}__alumno`">
        <div :class="`${PREFIX}__cabecera`">
          <span :class="`${PREFIX}__avatar`" aria-hidden="true">{{
            alumno.nombre.charAt(0).toUpperCase()
          }}</span>
          <div>
            <h3 :class="`${PREFIX}__nombre`">{{ alumno.nombre }}</h3>
            <p :class="`${PREFIX}__posicion`">{{ alumno.posicion }}</p>
          </div>
        </div>
        <v-barra-dato
          etiqueta="Avance de la tarea"
          :valor="alumno.avance"
          :valor-texto="`${alumno.avance} %`"
          :tono="alumno.alerta?.tipo === 'se-traba' ? 'aviso' : 'marca'"
        />
        <v-chip
          v-if="alumno.alerta"
          :class="`${PREFIX}__alerta`"
          :tono="ALERTA_ALUMNO[alumno.alerta.tipo].tono"
          :icono="ALERTA_ALUMNO[alumno.alerta.tipo].icono"
        >
          {{ alumno.alerta.texto }}
        </v-chip>
        <p :class="`${PREFIX}__nota`">{{ alumno.nota }}</p>
        <v-button
          variante="secundario"
          bloque
          :destino="{ name: RutaEnum.ALUMNO, params: { alias: alumno.alias } }"
        >
          Ver detalle de {{ alumno.nombre.split(" ")[0] }}
        </v-button>
      </li>
    </ul>
  </section>
</template>

<script src="./cmp-mi-clase.ts" lang="ts"></script>

<style src="./cmp-mi-clase.scss" lang="scss" scoped></style>
