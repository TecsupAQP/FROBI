<template>
  <div :class="PREFIX">
    <v-chip tono="marino">Paso 3 · Docente</v-chip>
    <cmp-encabezado-pagina
      :titulo="`Nueva clase: ${nombreCorto || 'sin nombre'}`"
      :descripcion="`${estudiante?.alias ?? 'Docente'} · Mecatrónica · ciclo 1`"
    />

    <div :class="`${PREFIX}__columnas`">
      <div :class="`${PREFIX}__principal`">
        <section :class="`${PREFIX}__tarjeta`" aria-labelledby="clase-contenido">
          <h2 id="clase-contenido" :class="`${PREFIX}__titulo`">Contenido de la clase</h2>
          <p v-if="!materiales.length" :class="`${PREFIX}__vacio`">
            Sube la guía o los PDF de tu clase. FROBI los adapta para cada estudiante.
          </p>
          <ul v-else :class="`${PREFIX}__materiales`">
            <li v-for="material in materiales" :key="material" :class="`${PREFIX}__material`">
              <v-icon nombre="file" />
              <div :class="`${PREFIX}__material-textos`">
                <p :class="`${PREFIX}__material-nombre`">{{ material }}</p>
                <v-chip tono="exito" icono="check">Se sube al crear la clase</v-chip>
              </div>
            </li>
          </ul>
          <v-button variante="secundario" bloque aria-haspopup="dialog" @click="abrirModal">{{
            materiales.length ? "Subir otro archivo" : "Subir un archivo"
          }}</v-button>
        </section>

        <section :class="`${PREFIX}__tarjeta`" aria-labelledby="clase-ia">
          <h2 id="clase-ia" :class="`${PREFIX}__titulo`">Cómo ayuda la IA en esta clase</h2>
          <ul :class="`${PREFIX}__reglas`">
            <li v-for="regla in REGLAS" :key="regla">
              <v-icon nombre="check" :tamano="20" />
              {{ regla }}
            </li>
          </ul>
        </section>
      </div>

      <form :class="`${PREFIX}__formulario`" novalidate @submit.prevent="crearYSeguir">
        <v-field
          id="clase-nombre"
          v-model="nombre"
          etiqueta="Nombre de la clase"
          placeholder="Ej. Física 1 · Mecatrónica"
          :error="errorNombre"
        />
        <v-field
          id="clase-tarea"
          v-model="primeraTarea"
          etiqueta="Primera tarea"
          placeholder="Ej. Resolver los ejercicios del tema 1"
        />
        <v-button tipo="submit" bloque :deshabilitado="ocupado">
          {{ ocupado ? "Creando clase…" : "Crear clase e invitar alumnos" }}
        </v-button>
      </form>
    </div>

    <cmp-subir-pdf
      v-model="modalAbierto"
      :fase="fase"
      :progreso="progreso"
      :nombre-archivo="nombreArchivo"
      :tamano-archivo-mb="tamanoArchivoMb"
      :archivo="archivo"
      @elegir="elegirArchivo"
      @cancelar="cancelarSubida"
      @usar="agregarMaterial"
    />
  </div>
</template>

<script src="./cmp-clase-nueva.ts" lang="ts"></script>

<style src="./cmp-clase.scss" lang="scss" scoped></style>
