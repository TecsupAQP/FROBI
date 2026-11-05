<template>
  <div :class="PREFIX">
    <cmp-encabezado-pagina
      titulo="Revisa tu borrador"
      descripcion="Marcamos lo que conviene verificar según tu material. No decimos si lo escribió una IA."
    />

    <div v-if="!revision" :class="`${PREFIX}__cargando`">
      <v-cargando>Revisando tu trabajo…</v-cargando>
    </div>

    <template v-else>
      <ul :class="`${PREFIX}__resumen`" aria-label="Resumen de la revisión">
        <li v-for="estado in ESTADOS" :key="estado">
          <v-semaforo :estado="estado">{{
            SEMAFORO[estado].textoConteo(revision.resumen[estado])
          }}</v-semaforo>
        </li>
      </ul>

      <div :class="`${PREFIX}__columnas`">
        <div :class="`${PREFIX}__secciones`">
          <cmp-seccion-revisada v-for="seccion in revision.secciones" :key="seccion.id" :seccion="seccion" />
        </div>

        <aside :class="`${PREFIX}__siguiente`" :aria-labelledby="`${PREFIX}-siguiente`">
          <h2 :id="`${PREFIX}-siguiente`" :class="`${PREFIX}__siguiente-titulo`">Siguiente paso</h2>
          <p>
            Verifica lo que no tiene respaldo en tu material. Te recomendamos una herramienta y cómo pedirla.
          </p>
          <v-button bloque :destino="{ name: RutaEnum.HERRAMIENTAS }">Ver cómo verificarla</v-button>
          <v-button bloque variante="secundario" :destino="{ name: RutaEnum.TRAE_TU_TRABAJO }">
            Volver a mi borrador
          </v-button>
          <v-aviso tipo="nota">La IA puede equivocarse; contrasta con tu guía.</v-aviso>
        </aside>
      </div>
    </template>
  </div>
</template>

<script src="./cmp-revision.ts" lang="ts"></script>

<style src="./cmp-revision.scss" lang="scss" scoped></style>
