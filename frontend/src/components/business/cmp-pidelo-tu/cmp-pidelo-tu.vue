<template>
  <div :class="PREFIX">
    <cmp-encabezado-pagina
      titulo="Pídelo tú"
      :descripcion="descripcion"
      :volver="{
        texto: 'Volver al resultado',
        destino: { name: RutaEnum.RESULTADO, params: { formato: 'mapa-visual' } },
      }"
    />

    <cmp-autonomia v-if="autonomia" :autonomia="autonomia" />

    <div v-if="fase === 'escribiendo' || fase === 'evaluando'" :class="`${PREFIX}__columnas`">
      <cmp-editor-instruccion
        v-model="instruccion"
        :class="`${PREFIX}__principal`"
        etiqueta="Escribe cómo quieres que la IA te explique"
        :piezas-escritas="piezasEscritas"
        :puede-pedir="puedePedir"
        :ocupado="fase === 'evaluando'"
        @pedir="pedirALaIA"
      />
      <cmp-plantilla :class="`${PREFIX}__lateral`" :plantilla="plantilla" @usar="usarPlantilla" />
    </div>

    <div v-else-if="(fase === 'debil' || fase === 'mejorando') && evaluacion" :class="`${PREFIX}__columnas`">
      <div :class="`${PREFIX}__principal`">
        <cmp-editor-instruccion
          v-model="instruccion"
          etiqueta="Tu instrucción"
          :piezas-escritas="piezasEscritas"
          :ocupado="fase === 'mejorando'"
          compacto
        />
        <cmp-sugerencia
          v-if="evaluacion.sugerencia"
          :sugerencia="evaluacion.sugerencia"
          :ocupado="fase === 'mejorando'"
          @mejorar="mejorarInstruccion"
          @anadir="anadirEjemplo"
        />
      </div>
      <cmp-puntaje-piezas :class="`${PREFIX}__lateral`" :evaluacion="evaluacion" />
    </div>

    <template v-else-if="fase === 'comparacion' && evaluacion && mejorada">
      <cmp-comparacion :evaluacion="evaluacion" :mejorada="mejorada" />
      <cmp-resultado-mejorada :resultado="mejorada.resultado" @copiar="copiarReceta" @probar="probarOtra" />
    </template>

    <section :class="`${PREFIX}__sin-ia`" aria-labelledby="pidelo-sin-ia">
      <h2 id="pidelo-sin-ia" :class="`${PREFIX}__sin-ia-titulo`">¿Prefieres practicar sin IA?</h2>
      <p>Resolver solo también cuenta. Tu docente lo ve como un logro.</p>
      <v-button variante="secundario" :destino="{ name: RutaEnum.SIN_IA, params: { tarea: TAREA_EJEMPLO } }">
        Intentarlo sin IA
      </v-button>
    </section>
  </div>
</template>

<script src="./cmp-pidelo-tu.ts" lang="ts"></script>

<style src="./cmp-pidelo-tu.scss" lang="scss" scoped></style>
