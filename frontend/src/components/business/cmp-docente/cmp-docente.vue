<template>
  <div :class="PREFIX">
    <div v-if="!panel" :class="`${PREFIX}__cargando`">
      <v-cargando>Cargando el panel…</v-cargando>
    </div>

    <template v-else>
      <v-chip tono="marino" :class="`${PREFIX}__paso`">Paso 8 · Docente ve avances</v-chip>
      <cmp-encabezado-pagina
        titulo="Panel docente"
        :descripcion="`${panel.grupo.nombre} · ${panel.grupo.estudiantes} estudiantes (solo alias, sin datos personales)`"
      >
        <template #acciones>
          <v-select
            id="docente-grupo"
            :class="`${PREFIX}__grupo`"
            :model-value="grupoId"
            etiqueta="Grupo"
            :opciones="panel.grupos"
            @update:model-value="cambiarGrupo"
          />
        </template>
      </cmp-encabezado-pagina>

      <cmp-mi-clase v-if="clase" :clase="clase" />

      <v-aviso v-if="panel.esEjemplo" :class="`${PREFIX}__ejemplo`" tipo="aviso" icono="info">
        Maqueta con datos de ejemplo. Visible solo para el rol Docente.
      </v-aviso>

      <div :class="`${PREFIX}__tarjetas`">
        <section :class="`${PREFIX}__tarjeta`" aria-labelledby="docente-formatos">
          <div>
            <h2 id="docente-formatos" :class="`${PREFIX}__titulo`">Formatos más pedidos</h2>
            <p :class="`${PREFIX}__secundario`">Del total de adaptaciones del grupo</p>
          </div>
          <v-barra-dato
            v-for="dato in panel.formatosPedidos"
            :key="dato.etiqueta"
            :etiqueta="dato.etiqueta"
            :valor="dato.porcentaje"
            :valor-texto="`${dato.porcentaje} %`"
          />
        </section>

        <section :class="`${PREFIX}__tarjeta`" aria-labelledby="docente-preguntas">
          <div>
            <h2 id="docente-preguntas" :class="`${PREFIX}__titulo`">Preguntas más falladas</h2>
            <p :class="`${PREFIX}__secundario`">Porcentaje del grupo que falló</p>
          </div>
          <v-barra-dato
            v-for="dato in panel.preguntasFalladas"
            :key="dato.etiqueta"
            :etiqueta="dato.etiqueta"
            :valor="dato.porcentaje"
            :valor-texto="`${dato.porcentaje} %`"
            tono="error"
          />
        </section>

        <section :class="`${PREFIX}__tarjeta`" aria-labelledby="docente-temas">
          <div>
            <h2 id="docente-temas" :class="`${PREFIX}__titulo`">Temas donde más se traban</h2>
            <p :class="`${PREFIX}__secundario`">Porcentaje que repite el tema o pide ayuda</p>
          </div>
          <v-barra-dato
            v-for="dato in panel.temasDificiles"
            :key="dato.etiqueta"
            :etiqueta="dato.etiqueta"
            :valor="dato.porcentaje"
            :valor-texto="`${dato.porcentaje} %`"
            tono="aviso"
          />
          <p :class="`${PREFIX}__sugerencia`">
            <v-icon nombre="bulb" :tamano="22" />
            {{ panel.sugerencia }}
          </p>
        </section>
      </div>

      <section :class="`${PREFIX}__tarjeta ${PREFIX}__uso`" aria-labelledby="docente-uso">
        <div>
          <h2 id="docente-uso" :class="`${PREFIX}__titulo`">Uso de IA y competencias en IA</h2>
          <p :class="`${PREFIX}__secundario`">
            Solo cuenta lo que ocurre dentro de FROBI. Las herramientas externas se registran si el estudiante
            las declara.
          </p>
        </div>
        <div :class="`${PREFIX}__uso-columnas`">
          <div :class="`${PREFIX}__bloque`">
            <h3 :class="`${PREFIX}__bloque-titulo`">Uso de IA dentro de FROBI</h3>
            <p :class="`${PREFIX}__promedio`">
              <span :class="`${PREFIX}__promedio-valor`">{{
                String(panel.actividadesPromedio).replace(".", ",")
              }}</span>
              actividades por estudiante, en promedio
            </p>
            <v-barra-dato
              v-for="dato in panel.usoIa"
              :key="dato.etiqueta"
              :etiqueta="dato.etiqueta"
              :valor="dato.valor"
              :maximo="dato.total"
              :valor-texto="`${dato.valor} de ${dato.total}`"
            />
          </div>
          <div :class="`${PREFIX}__bloque`">
            <h3 :class="`${PREFIX}__bloque-titulo`">Competencias en IA</h3>
            <v-barra-dato
              v-for="dato in panel.competencias"
              :key="dato.etiqueta"
              :etiqueta="dato.etiqueta"
              :valor="dato.porcentaje"
              :valor-texto="`${dato.porcentaje} %`"
            />
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script src="./cmp-docente.ts" lang="ts"></script>

<style src="./cmp-docente.scss" lang="scss" scoped></style>
