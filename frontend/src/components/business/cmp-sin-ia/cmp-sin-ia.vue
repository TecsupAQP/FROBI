<template>
  <div :class="PREFIX">
    <div v-if="!tarea" :class="`${PREFIX}__cargando`">
      <v-cargando>Preparando la tarea…</v-cargando>
    </div>

    <template v-else>
      <v-chip tono="marca">Paso 7 · Estudiante</v-chip>
      <cmp-encabezado-pagina
        titulo="Inténtalo sin IA"
        descripcion="Resuélvelo con tus palabras. Después compara con tu guía."
      />

      <div :class="`${PREFIX}__columnas`">
        <div :class="`${PREFIX}__principal`">
          <section :class="`${PREFIX}__tarjeta`" aria-labelledby="sin-ia-enunciado">
            <h2 id="sin-ia-enunciado" :class="`${PREFIX}__enunciado`">{{ tarea.enunciado }}</h2>
            <v-field
              id="sin-ia-respuesta"
              :model-value="progreso.respuestaSinIa"
              etiqueta="Tu respuesta"
              placeholder="Escribe aquí con tus palabras"
              multilinea
              :filas="3"
              @update:model-value="escribirRespuestaSinIa"
            />
          </section>

          <section :class="`${PREFIX}__tarjeta`" aria-labelledby="sin-ia-autoevaluacion">
            <h2 id="sin-ia-autoevaluacion" :class="`${PREFIX}__titulo`">Autoevaluación</h2>
            <fieldset :class="`${PREFIX}__criterios`">
              <legend class="solo-lector">Marca lo que hiciste</legend>
              <v-casilla
                v-for="criterio in criterios"
                :key="criterio"
                :model-value="progreso.criteriosMarcados.includes(criterio)"
                @update:model-value="alternarCriterio(criterio)"
              >
                {{ criterio }}
              </v-casilla>
            </fieldset>
            <v-button bloque :deshabilitado="!progreso.respuestaSinIa.trim() || probando" @click="comparar">
              {{ probando ? "Comparando con tu guía…" : "Comparar con mi guía" }}
            </v-button>
            <div v-if="comparado" :class="`${PREFIX}__guia`" role="status">
              <p :class="`${PREFIX}__guia-titulo`">Tu guía dice</p>
              <p v-for="pasaje in progreso.pasajesGuia" :key="pasaje">«{{ pasaje }}»</p>
              <p v-if="!progreso.pasajesGuia.length">
                No encontramos en tu guía una parte que hable de lo que escribiste. Vuelve a leerla y revisa
                tu respuesta.
              </p>
              <p :class="`${PREFIX}__secundario`">Compara con lo que escribiste y corrige si hace falta.</p>
            </div>
            <p v-if="error" :class="`${PREFIX}__secundario`" role="alert">{{ error }}</p>
          </section>
        </div>

        <aside :class="`${PREFIX}__lateral`" aria-labelledby="sin-ia-logro">
          <h2 id="sin-ia-logro" :class="`${PREFIX}__titulo`">Cuenta como logro</h2>
          <v-chip
            :tono="progreso.resueltoSinIa ? 'exito' : 'neutro'"
            :icono="progreso.resueltoSinIa ? 'check' : 'clock'"
          >
            {{ progreso.resueltoSinIa ? "Resuelto sin IA" : "Aún sin resolver" }}
          </v-chip>
          <p :class="`${PREFIX}__texto`">
            Tu docente ve que lo intentaste sin ayuda. Usar la IA a veces y practicar solo también es
            aprender.
          </p>
          <v-button
            variante="secundario"
            bloque
            :destino="{ name: RutaEnum.AYUDA, params: { tarea: tarea.id } }"
          >
            Pedir una pista
          </v-button>
        </aside>
      </div>
    </template>
  </div>
</template>

<script src="./cmp-sin-ia.ts" lang="ts"></script>

<style src="./cmp-sin-ia.scss" lang="scss" scoped></style>
