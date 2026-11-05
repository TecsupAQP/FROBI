<template>
  <section :class="PREFIX" aria-labelledby="contenido-clase-titulo">
    <div :class="`${PREFIX}__cabecera`">
      <div>
        <h2 id="contenido-clase-titulo" :class="`${PREFIX}__titulo`">Guías de la clase</h2>
        <p :class="`${PREFIX}__secundario`">
          Cada guía es de estudio (la IA evalúa al final) o tiene tareas que tú escribes. Tus alumnos la ven
          en su Inicio con su avance.
        </p>
      </div>
      <v-button
        v-if="!creando"
        icono="upload"
        variante="secundario"
        :deshabilitado="subiendo"
        @click="abrirNueva"
      >
        {{ subiendo ? "Subiendo…" : "Subir guía" }}
      </v-button>
    </div>

    <p v-if="error" :class="`${PREFIX}__error`" role="alert">
      <v-icon nombre="alert" :tamano="20" />
      {{ error }}
    </p>

    <div v-if="creando" :class="`${PREFIX}__nueva`">
      <h3 :class="`${PREFIX}__subtitulo`">Nueva guía</h3>
      <div :class="`${PREFIX}__archivo`">
        <v-button variante="secundario" icono="file" @click="abrirSelector">
          {{ archivo ? "Cambiar PDF" : "Elegir PDF" }}
        </v-button>
        <p :class="`${PREFIX}__secundario`" aria-live="polite">
          {{ archivo ? archivo.name : "PDF con texto, de hasta 10 MB." }}
        </p>
      </div>
      <cmp-plan-guia
        prefijo-id="nueva-guia"
        :modo="modo"
        :tareas="tareas"
        @update:modo="modo = $event"
        @update:tareas="tareas = $event"
      />
      <div :class="`${PREFIX}__acciones`">
        <v-button icono="upload" :deshabilitado="!puedeSubir" @click="subir">Subir guía</v-button>
        <v-button variante="texto" @click="creando = false">Cancelar</v-button>
      </div>
    </div>

    <p v-if="!materiales.length && !creando" :class="`${PREFIX}__vacio`">
      Todavía no subiste guías. Sube el PDF de tu curso y elige si es de estudio o con tareas.
    </p>
    <ul v-else-if="materiales.length" :class="`${PREFIX}__lista`" aria-live="polite">
      <li v-for="material in materiales" :key="material.id" :class="`${PREFIX}__material`">
        <div :class="`${PREFIX}__fila`">
          <span :class="`${PREFIX}__icono`" aria-hidden="true"><v-icon nombre="file" :tamano="22" /></span>
          <div :class="`${PREFIX}__textos`">
            <h3 :class="`${PREFIX}__nombre`">{{ material.titulo }}</h3>
            <p :class="`${PREFIX}__fecha`">Subida el {{ formatearFecha(material.fecha) }}</p>
            <v-chip :tono="material.modo === 'tareas' ? 'marino' : 'suave'" icono="book">
              {{
                material.modo === "tareas"
                  ? `Con ${material.tareas.length} ${material.tareas.length === 1 ? "tarea" : "tareas"}`
                  : "De estudio · evaluación final"
              }}
            </v-chip>
          </div>
          <v-button
            v-if="editando !== material.id"
            variante="texto"
            icono="pencil"
            :deshabilitado="guardando === material.id"
            :etiqueta="`Editar la guía ${material.titulo}`"
            @click="editar(material)"
          >
            {{ guardando === material.id ? "Guardando…" : "Editar" }}
          </v-button>
        </div>

        <div v-if="editando === material.id" :class="`${PREFIX}__edicion`">
          <cmp-plan-guia
            :modo="modoEdicion"
            :tareas="tareasEdicion"
            :prefijo-id="`guia-${material.id}`"
            @update:modo="modoEdicion = $event"
            @update:tareas="tareasEdicion = $event"
          />
          <p :class="`${PREFIX}__secundario`">
            Las tareas que no cambies conservan lo que tus alumnos ya hicieron.
          </p>
          <div :class="`${PREFIX}__acciones`">
            <v-button
              icono="save"
              :deshabilitado="!planValido(modoEdicion, tareasEdicion)"
              @click="guardar(material.id)"
            >
              Guardar cambios
            </v-button>
            <v-button variante="texto" @click="editando = null">Cancelar</v-button>
          </div>
        </div>

        <ol v-else-if="material.modo === 'tareas'" :class="`${PREFIX}__tareas`">
          <li v-for="tarea in material.tareas" :key="tarea.id">{{ tarea.enunciado }}</li>
        </ol>

        <div :class="`${PREFIX}__avance`">
          <h4 :class="`${PREFIX}__avance-titulo`">Avance de tus alumnos</h4>
          <p v-if="!avanceDe(material.id).length" :class="`${PREFIX}__secundario`">
            Aún no hay alumnos unidos a la clase.
          </p>
          <v-barra-dato
            v-for="alumno in avanceDe(material.id)"
            :key="alumno.personaId"
            :etiqueta="alumno.alias"
            :valor="alumno.avance"
            :valor-texto="`${alumno.avance} %`"
          />
        </div>
      </li>
    </ul>

    <input
      ref="selector"
      class="solo-lector"
      type="file"
      accept="application/pdf,.pdf"
      tabindex="-1"
      aria-hidden="true"
      @change="alElegir"
    />
  </section>
</template>

<script src="./cmp-contenido-clase.ts" lang="ts"></script>

<style src="./cmp-contenido-clase.scss" lang="scss" scoped></style>
