<template>
  <div :class="PREFIX">
    <div v-if="cargando" :class="`${PREFIX}__cargando`">
      <v-cargando>Cargando la actividad del alumno…</v-cargando>
    </div>

    <v-estado-vacio
      v-else-if="!detalle"
      icono="users"
      titulo="No encontramos a este alumno"
      texto="Solo ves a los alumnos de tu clase."
    >
      <v-button :destino="{ name: RutaEnum.DOCENTE }">Volver al panel</v-button>
    </v-estado-vacio>

    <template v-else>
      <v-chip tono="marino">Paso 9 · Docente</v-chip>
      <cmp-encabezado-pagina
        :titulo="detalle.alumno.nombre"
        :descripcion="`${detalle.clase} · último acceso ${detalle.ultimoAcceso}`"
        :volver="{ texto: 'Volver al panel', destino: { name: RutaEnum.DOCENTE } }"
      />
      <v-aviso tipo="aviso" icono="info">
        Datos de ejemplo. Solo ves la actividad de {{ detalle.alumno.nombre.split(" ")[0] }} dentro de esta
        clase.
      </v-aviso>

      <div :class="`${PREFIX}__columnas`">
        <div :class="`${PREFIX}__principal`">
          <section :class="`${PREFIX}__tarjeta`" aria-labelledby="alumno-escalera">
            <h2 id="alumno-escalera" :class="`${PREFIX}__titulo`">Cómo usó la escalera de ayuda</h2>
            <ul :class="`${PREFIX}__usos`">
              <li v-for="uso in detalle.usoEscalera" :key="uso.texto" :class="`${PREFIX}__uso`">
                <v-icon
                  :class="uso.usado ? `${PREFIX}__usado` : `${PREFIX}__sin-uso`"
                  :nombre="uso.usado ? 'check' : 'minus'"
                  :tamano="20"
                  :etiqueta="uso.usado ? 'Usado' : 'No usado'"
                />
                {{ uso.texto }}
              </li>
            </ul>
            <v-barra-dato
              etiqueta="Ejercicios resueltos sin IA"
              :valor="detalle.resueltosSinIa.hechos"
              :maximo="detalle.resueltosSinIa.total"
              :valor-texto="`${detalle.resueltosSinIa.hechos} de ${detalle.resueltosSinIa.total}`"
            />
          </section>

          <section :class="`${PREFIX}__tarjeta`" aria-labelledby="alumno-competencias">
            <h2 id="alumno-competencias" :class="`${PREFIX}__titulo`">Competencias en IA</h2>
            <v-barra-dato
              v-for="competencia in detalle.competencias"
              :key="competencia.etiqueta"
              :etiqueta="competencia.etiqueta"
              :valor="competencia.porcentaje"
              :valor-texto="`${competencia.porcentaje} %`"
            />
          </section>
        </div>

        <div :class="`${PREFIX}__lateral`">
          <section :class="`${PREFIX}__tarjeta`" aria-labelledby="alumno-conversacion">
            <h2 id="alumno-conversacion" :class="`${PREFIX}__titulo`">Conversación (resumen)</h2>
            <ol :class="`${PREFIX}__mensajes`">
              <li
                v-for="(mensaje, indice) in mensajesVisibles"
                :key="indice"
                :class="[`${PREFIX}__mensaje`, `${PREFIX}__mensaje--${mensaje.autor}`]"
              >
                <p :class="`${PREFIX}__mensaje-autor`">{{ mensaje.etiqueta }}</p>
                <p>{{ mensaje.texto }}</p>
              </li>
            </ol>
            <v-button variante="secundario" bloque :aria-expanded="completa" @click="completa = !completa">
              {{ completa ? "Ver solo el resumen" : "Ver conversación completa" }}
            </v-button>
          </section>

          <section :class="`${PREFIX}__sugerencia`" aria-labelledby="alumno-sugerencia">
            <h2 id="alumno-sugerencia" :class="`${PREFIX}__sugerencia-titulo`">
              <v-icon nombre="bulb" :tamano="22" />
              Sugerencia para ti
            </h2>
            <p>{{ detalle.sugerencia }}</p>
          </section>
        </div>
      </div>
    </template>
  </div>
</template>

<script src="./cmp-alumno.ts" lang="ts"></script>

<style src="./cmp-alumno.scss" lang="scss" scoped></style>
