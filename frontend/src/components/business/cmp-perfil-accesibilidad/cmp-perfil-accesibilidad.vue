<template>
  <div :class="PREFIX">
    <v-chip tono="marca" :class="`${PREFIX}__paso`">Paso 5 · Estudiante</v-chip>
    <cmp-encabezado-pagina
      titulo="¿Cómo aprendes mejor?"
      descripcion="Elige lo que te ayuda. FROBI adapta formatos y ayudas. Es opcional y puedes cambiarlo cuando quieras."
    />

    <div :class="`${PREFIX}__columnas`">
      <fieldset :class="`${PREFIX}__opciones`">
        <legend class="solo-lector">Perfiles de accesibilidad (puedes elegir varios)</legend>
        <v-casilla
          v-for="opcion in PERFILES_ACCESIBILIDAD"
          :key="opcion.id"
          :model-value="perfil.perfiles.includes(opcion.id)"
          :icono="opcion.icono"
          :descripcion="opcion.descripcion"
          @update:model-value="alternarPerfil(opcion.id)"
        >
          {{ opcion.nombre }}
        </v-casilla>
      </fieldset>

      <div :class="`${PREFIX}__lateral`">
        <section :class="`${PREFIX}__cambios`" aria-labelledby="perfil-cambios" aria-live="polite">
          <h2 id="perfil-cambios" :class="`${PREFIX}__titulo`">Así cambiará tu pantalla</h2>
          <ul v-if="cambios.length" :class="`${PREFIX}__lista`">
            <li v-for="cambio in cambios" :key="cambio">
              <v-icon nombre="check" :tamano="20" />
              {{ cambio }}
            </li>
          </ul>
          <p v-else :class="`${PREFIX}__secundario`">
            Sin cambios: elige una opción para ver cómo se adapta.
          </p>
        </section>
        <v-button bloque :deshabilitado="guardando" @click="guardarYSeguir">Guardar y continuar</v-button>
        <v-button bloque variante="secundario" @click="seguir">Omitir por ahora</v-button>
      </div>
    </div>
  </div>
</template>

<script src="./cmp-perfil-accesibilidad.ts" lang="ts"></script>

<style src="./cmp-perfil-accesibilidad.scss" lang="scss" scoped></style>
