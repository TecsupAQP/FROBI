<template>
  <div :class="PREFIX">
    <cmp-encabezado-pagina
      titulo="Trae tu trabajo"
      descripcion="Pega la consigna de tu profesor y tu borrador. FROBI los organiza; no dice qué parte escribió una IA."
    />

    <div :class="`${PREFIX}__columnas`">
      <form :class="`${PREFIX}__formulario`" aria-label="Tu material" @submit.prevent="revisarYContinuar">
        <v-field
          id="trabajo-consigna"
          v-model="consigna"
          etiqueta="Consigna del profesor"
          tamano="grande"
          multilinea
          :filas="3"
        />
        <v-field
          id="trabajo-borrador"
          v-model="borrador"
          etiqueta="Tu borrador"
          tamano="grande"
          multilinea
          :filas="5"
        />
        <p :class="`${PREFIX}__conteo`" aria-live="polite">
          <v-icon nombre="file" :tamano="20" />
          Borrador: {{ palabras }} palabras
        </p>
        <v-cargando v-if="revisando">Revisando tu trabajo…</v-cargando>
        <div v-else :class="`${PREFIX}__acciones`">
          <v-button tipo="submit" :deshabilitado="!puedeRevisar">Revisar mi trabajo</v-button>
          <v-button variante="secundario" aria-haspopup="dialog" @click="abrirModal">Subir un PDF</v-button>
        </div>
      </form>
      <cmp-pasos-siguientes :class="`${PREFIX}__lateral`" />
    </div>

    <cmp-subir-pdf
      v-model="modalAbierto"
      :fase="fase"
      :progreso="progreso"
      :nombre-archivo="nombreArchivo"
      :tamano-archivo-mb="tamanoArchivoMb"
      :archivo="archivo"
      @elegir="elegirArchivo()"
      @cancelar="cancelarSubida"
      @usar="usarPdf"
    />
  </div>
</template>

<script src="./cmp-trae-trabajo.ts" lang="ts"></script>

<style src="./cmp-trae-trabajo.scss" lang="scss" scoped></style>
