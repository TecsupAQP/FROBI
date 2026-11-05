<template>
  <v-modal id="subir-pdf" v-model="abierto" titulo="Subir mi PDF">
    <template v-if="fase === 'subiendo'">
      <div :class="`${PREFIX}__archivo`">
        <v-icon nombre="file" />
        <div>
          <p :class="`${PREFIX}__archivo-nombre`">{{ nombreArchivo }}</p>
          <p :class="`${PREFIX}__archivo-detalle`">{{ String(tamanoArchivoMb).replace(".", ",") }} MB</p>
        </div>
      </div>
      <div :class="`${PREFIX}__progreso`">
        <v-progress-bar :valor="progreso" etiqueta="Leyendo tu PDF" />
        <p :class="`${PREFIX}__progreso-texto`" aria-live="polite">Leyendo tu PDF… {{ progreso }} %</p>
      </div>
      <v-button :class="`${PREFIX}__cancelar`" variante="secundario" @click="$emit('cancelar')"
        >Cancelar</v-button
      >
    </template>

    <template v-else-if="fase === 'error' && !pegando">
      <div :class="`${PREFIX}__error`" role="alert">
        <v-icon nombre="alert" :tamano="28" />
        <p :class="`${PREFIX}__error-titulo`">No pudimos leer este PDF</p>
        <p>Parece una imagen escaneada. Prueba con un PDF con texto seleccionable o pega el texto aquí.</p>
      </div>
      <div :class="`${PREFIX}__acciones-error`">
        <v-button @click="$emit('elegir')">Elegir otro PDF</v-button>
        <v-button variante="secundario" @click="pegando = true">Pegar el texto</v-button>
      </div>
    </template>

    <template v-else-if="pegando">
      <v-field
        id="subir-pdf-texto"
        v-model="textoPegado"
        etiqueta="Pega el texto de tu guía"
        placeholder="Copia el texto del PDF y pégalo aquí…"
        multilinea
        :filas="8"
      />
    </template>

    <template v-else>
      <p :class="`${PREFIX}__intro`">
        Elige el PDF de tu curso. Te mostramos el texto que leímos para que lo revises.
      </p>
      <div :class="`${PREFIX}__zona`">
        <v-icon :class="`${PREFIX}__zona-icono`" nombre="upload" :tamano="32" />
        <p :class="`${PREFIX}__zona-texto`">Arrastra tu PDF aquí</p>
        <p :class="`${PREFIX}__zona-o`" aria-hidden="true">o</p>
        <v-button variante="secundario" @click="$emit('elegir')">
          {{ archivo ? "Elegir otro archivo" : "Elegir archivo" }}
        </v-button>
      </div>
      <template v-if="archivo">
        <div :class="`${PREFIX}__exito`">
          <v-icon nombre="check-circle" />
          <div>
            <p :class="`${PREFIX}__exito-nombre`">{{ archivo.nombre }} · {{ archivo.paginas }} páginas</p>
            <p :class="`${PREFIX}__exito-detalle`">Texto extraído correctamente</p>
          </div>
        </div>
        <section :class="`${PREFIX}__vista`" :aria-labelledby="`${PREFIX}-vista`">
          <h3 :id="`${PREFIX}-vista`" :class="`${PREFIX}__vista-titulo`">Vista previa del texto extraído</h3>
          <div :class="`${PREFIX}__texto`" tabindex="0" aria-label="Texto extraído del PDF">
            <p :class="`${PREFIX}__texto-titulo`">{{ archivo.vistaPrevia.titulo }}</p>
            <p>{{ archivo.vistaPrevia.texto }}</p>
          </div>
          <p :class="`${PREFIX}__privacidad`">Solo se usa para adaptar tu guía. No se comparte con nadie.</p>
        </section>
      </template>
    </template>

    <template v-if="(fase === 'listo' && archivo) || pegando" #pie>
      <v-button variante="secundario" @click="cancelar">Cancelar</v-button>
      <v-button :deshabilitado="pegando && !textoPegado.trim()" @click="$emit('usar')">
        {{ pegando ? "Usar este texto" : "Usar esta guía" }}
      </v-button>
    </template>
  </v-modal>
</template>

<script src="./cmp-subir-pdf.ts" lang="ts"></script>

<style src="./cmp-subir-pdf.scss" lang="scss" scoped></style>
