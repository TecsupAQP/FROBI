<template>
  <div :class="PREFIX">
    <cmp-encabezado-pagina
      titulo="Cómo verificar este dato"
      :descripcion="
        recomendacion
          ? `Para comprobar «${recomendacion.afirmacion}» te recomendamos esta herramienta.`
          : 'Buscando la herramienta adecuada…'
      "
    />

    <div v-if="!recomendacion" :class="`${PREFIX}__cargando`">
      <v-cargando>Cargando herramientas…</v-cargando>
    </div>

    <template v-else>
      <section
        v-if="recomendada"
        :class="`${PREFIX}__recomendada`"
        :aria-labelledby="`${PREFIX}-recomendada`"
        aria-live="polite"
      >
        <span :class="`${PREFIX}__etiqueta`">Recomendada para {{ nombreNecesidad.toLowerCase() }}</span>
        <div :class="`${PREFIX}__cabecera`">
          <span :class="`${PREFIX}__icono`" aria-hidden="true">
            <v-icon :nombre="recomendada.icono" :tamano="32" />
          </span>
          <h2 :id="`${PREFIX}-recomendada`" :class="`${PREFIX}__nombre`">{{ recomendada.nombre }}</h2>
        </div>
        <div :class="`${PREFIX}__motivos`">
          <div :class="`${PREFIX}__motivo ${PREFIX}__motivo--si`">
            <p :class="`${PREFIX}__motivo-titulo`">Por qué sirve</p>
            <p>{{ recomendada.porQueSirve }}</p>
          </div>
          <div :class="`${PREFIX}__motivo ${PREFIX}__motivo--no`">
            <p :class="`${PREFIX}__motivo-titulo`">Cuándo no usarla</p>
            <p>{{ recomendada.cuandoNoUsarla }}</p>
          </div>
        </div>
        <div :class="`${PREFIX}__acciones`">
          <v-button :destino="{ name: RutaEnum.PIDELO_TU }">Escribir mi instrucción de verificación</v-button>
          <v-button variante="secundario" :destino="{ name: RutaEnum.TRAE_TU_TRABAJO }"
            >Volver a mi borrador</v-button
          >
        </div>
      </section>

      <div :class="`${PREFIX}__filtro`" role="group" :aria-labelledby="`${PREFIX}-filtro`">
        <p :id="`${PREFIX}-filtro`" :class="`${PREFIX}__filtro-titulo`">
          Ver otras herramientas según lo que necesitas
        </p>
        <ul :class="`${PREFIX}__chips`">
          <li v-for="item in recomendacion.necesidades" :key="item.id">
            <button
              type="button"
              :class="[`${PREFIX}__chip`, { [`${PREFIX}__chip--activa`]: item.id === necesidad }]"
              :aria-pressed="item.id === necesidad"
              @click="elegirNecesidad(item.id)"
            >
              <v-icon v-if="item.id === necesidad" nombre="check" :tamano="18" />
              {{ item.nombre }}
            </button>
          </li>
        </ul>
      </div>

      <ul :class="`${PREFIX}__catalogo`" aria-label="Otras herramientas">
        <li v-for="herramienta in otras" :key="herramienta.id">
          <cmp-tarjeta-herramienta :herramienta="herramienta" />
        </li>
      </ul>

      <v-aviso tipo="nota"
        >Catálogo fijo de la demo: 5 tipos de herramienta. FROBI recomienda, tú decides.</v-aviso
      >
    </template>
  </div>
</template>

<script src="./cmp-herramientas.ts" lang="ts"></script>

<style src="./cmp-herramientas.scss" lang="scss" scoped></style>
