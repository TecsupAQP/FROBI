<template>
  <div :class="PREFIX">
    <v-chip tono="marino">Paso 4 · Docente</v-chip>
    <cmp-encabezado-pagina
      titulo="Invita a tus alumnos"
      descripcion="Comparte el código o el enlace. También puedes invitar por alias."
    />

    <div v-if="!clase" :class="`${PREFIX}__cargando`">
      <v-cargando>Cargando la clase…</v-cargando>
    </div>

    <div v-else :class="`${PREFIX}__columnas`">
      <section
        data-recorrido="codigo"
        :class="[`${PREFIX}__tarjeta`, `${PREFIX}__principal`]"
        aria-labelledby="invitar-codigo"
      >
        <h2 id="invitar-codigo" :class="`${PREFIX}__titulo`">Código de la clase</h2>
        <p :class="`${PREFIX}__codigo`" aria-label="Código de la clase">{{ clase.codigo }}</p>
        <div :class="`${PREFIX}__acciones`">
          <v-button variante="secundario" @click="copiar(clase.codigo, 'Código copiado')"
            >Copiar código</v-button
          >
          <v-button variante="secundario" @click="copiar(enlace, 'Enlace copiado')">Copiar enlace</v-button>
        </div>
        <form :class="`${PREFIX}__correo`" novalidate @submit.prevent="enviar">
          <v-field
            id="invitar-correo"
            v-model="correo"
            etiqueta="O invita por alias"
            placeholder="ana_mecatronica"
            autocompletar="email"
            :error="errorCorreo"
          />
          <v-button tipo="submit" :deshabilitado="ocupado">{{
            ocupado ? "Enviando…" : "Enviar invitación"
          }}</v-button>
        </form>
      </section>

      <aside :class="`${PREFIX}__tarjeta`" aria-labelledby="invitar-lista">
        <h2 id="invitar-lista" :class="`${PREFIX}__titulo`">
          Alumnos invitados ({{ clase.alumnos.length }})
        </h2>
        <ul :class="`${PREFIX}__alumnos`" aria-live="polite">
          <li v-for="alumno in clase.alumnos" :key="alumno.alias"><cmp-alumno-item :alumno="alumno" /></li>
        </ul>
        <p :class="`${PREFIX}__privacidad`">
          <v-icon nombre="lock" :tamano="20" />
          Cada alumno ve que su docente puede ver su actividad en esta clase.
        </p>
        <v-button variante="secundario" bloque :destino="{ name: RutaEnum.DOCENTE }"
          >Ir al panel de la clase</v-button
        >
      </aside>
    </div>
  </div>
</template>

<script src="./cmp-clase-invitar.ts" lang="ts"></script>

<style src="./cmp-clase.scss" lang="scss" scoped></style>
