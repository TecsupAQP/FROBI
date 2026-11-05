<template>
  <div :class="PREFIX">
    <div v-if="!cargado" :class="`${PREFIX}__cargando`">
      <v-cargando>Cargando el panel…</v-cargando>
    </div>

    <v-estado-vacio
      v-else-if="!panel"
      icono="users"
      titulo="Todavía no tienes una clase"
      texto="Crea tu clase e invita a tus alumnos. Aquí verás su avance dentro de la clase."
    >
      <v-button :destino="{ name: RutaEnum.CLASE_NUEVA }">Crear mi clase</v-button>
    </v-estado-vacio>

    <template v-else>
      <v-chip tono="marino" :class="`${PREFIX}__paso`">Paso 8 · Docente ve avances</v-chip>
      <cmp-encabezado-pagina
        titulo="Panel docente"
        :descripcion="`${panel.grupo.nombre} · ${panel.grupo.estudiantes} estudiantes (solo alias, sin datos personales)`"
      >
        <template #acciones>
          <div :class="`${PREFIX}__clases`">
            <v-select
              id="docente-grupo"
              data-recorrido="selector-clase"
              :class="`${PREFIX}__grupo`"
              :model-value="grupoId"
              etiqueta="Clase"
              :opciones="panel.grupos"
              @update:model-value="cambiarGrupo"
            />
            <v-button variante="texto" icono="pencil" :destino="{ name: RutaEnum.CLASE_NUEVA }">
              Crear otra clase
            </v-button>
          </div>
        </template>
      </cmp-encabezado-pagina>

      <cmp-mi-clase v-if="clase" data-recorrido="mi-clase" :clase="clase" />

      <cmp-contenido-clase
        v-if="clase"
        data-recorrido="contenido-clase"
        :materiales="contenido"
        :subiendo="subiendo"
        :error="errorContenido"
        @subir="subirContenido"
      />

      <v-aviso v-if="panel.esEjemplo" :class="`${PREFIX}__ejemplo`" tipo="aviso" icono="info">
        Datos de ejemplo mientras tu clase no tenga actividad. Visible solo para el rol Docente.
      </v-aviso>

      <div data-recorrido="estadisticas" :class="`${PREFIX}__tarjetas`">
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

        <section
          v-if="panel.temasDificiles.length"
          :class="`${PREFIX}__tarjeta`"
          aria-labelledby="docente-temas"
        >
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
          <div v-if="panel.competencias.length" :class="`${PREFIX}__bloque`">
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
