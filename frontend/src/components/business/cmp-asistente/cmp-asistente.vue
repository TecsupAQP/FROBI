<template>
  <cmp-layout-asistente @omitir="terminar">
    <v-pasos :actual="paso" :total="3" nota="solo la primera vez" />

    <header :class="`${PREFIX}__encabezado`">
      <h1 :class="`${PREFIX}__titulo`">{{ PREGUNTAS[paso].titulo }}</h1>
      <p :class="`${PREFIX}__subtitulo`">{{ PREGUNTAS[paso].subtitulo }}</p>
    </header>

    <!-- Paso 1: quién usa FROBI -->
    <template v-if="paso === 1">
      <v-boton-escuchar :lectura="lecturaPregunta" />
      <div :class="`${PREFIX}__opciones`" role="radiogroup" aria-label="Quién va a usar FROBI">
        <v-opcion-tarjeta
          nombre="quien"
          titulo="Voy a usarlo yo"
          descripcion="Respondo yo las preguntas."
          icono="user"
          :elegida="perfil.configuradoPor === 'yo'"
          @elegir="elegirConfiguradoPor('yo')"
        />
        <v-opcion-tarjeta
          nombre="quien"
          titulo="Alguien me ayuda a configurarlo"
          descripcion="Una persona de confianza (familiar, docente o intérprete) responde por mí. Después aprendo por mi cuenta y ella no ve mi progreso."
          icono="users"
          :elegida="perfil.configuradoPor === 'acompanante'"
          @elegir="elegirConfiguradoPor('acompanante')"
        />
      </div>
      <v-button bloque @click="ir(2)">Continuar</v-button>
    </template>

    <!-- Paso 2: qué ayuda más -->
    <template v-else-if="paso === 2">
      <v-boton-escuchar :lectura="lecturaPregunta" />
      <fieldset :class="`${PREFIX}__grupo`">
        <legend class="solo-lector">Ayudas que quieres activar</legend>
        <div :class="`${PREFIX}__rejilla`">
          <v-opcion-tarjeta
            v-for="ajuste in AJUSTES_ACCESIBILIDAD"
            :key="ajuste.id"
            nombre="ayudas"
            multiple
            disposicion="compacta"
            :titulo="ajuste.nombreAsistente"
            :descripcion="ajuste.descripcionAsistente"
            :icono="ajuste.icono"
            :elegida="ajustes.activos[ajuste.id]"
            @elegir="elegirAyuda(ajuste.id)"
          />
        </div>
        <label :class="[`${PREFIX}__no-se`, { [`${PREFIX}__no-se--elegida`]: noLoSe }]">
          <input v-model="noLoSe" class="solo-lector" type="checkbox" @change="alElegirNoLoSe" />
          <v-icon nombre="help" :tamano="26" />
          <span>No lo sé: pruébalo conmigo</span>
          <v-icon v-if="noLoSe" :class="`${PREFIX}__check`" nombre="check" />
        </label>
      </fieldset>
      <div :class="`${PREFIX}__acciones`">
        <v-button variante="secundario" @click="ir(1)">Atrás</v-button>
        <v-button @click="ir(3)">Continuar</v-button>
      </div>
    </template>

    <!-- Paso 3: confirmación con vista previa -->
    <template v-else>
      <section :class="`${PREFIX}__vista`" aria-labelledby="asistente-vista">
        <h2 id="asistente-vista" :class="`${PREFIX}__vista-etiqueta`">Vista previa</h2>
        <p :class="`${PREFIX}__vista-paso`">Pista {{ pistaVista + 1 }} de {{ PISTAS_VISTA.length }}</p>
        <p :class="`${PREFIX}__vista-texto`" aria-live="polite">{{ PISTAS_VISTA[pistaVista] }}</p>
        <div :class="`${PREFIX}__vista-acciones`">
          <v-boton-escuchar :lectura="PISTAS_VISTA[pistaVista] ?? ''" texto="Escuchar" tono="suave" />
          <v-button @click="pistaVista = (pistaVista + 1) % PISTAS_VISTA.length">Siguiente pista</v-button>
        </div>
      </section>
      <section :class="`${PREFIX}__activamos`" aria-labelledby="asistente-activamos">
        <h2 id="asistente-activamos" :class="`${PREFIX}__subtitulo-seccion`">Lo que activamos</h2>
        <ul v-if="activados.length" :class="`${PREFIX}__lista`">
          <li v-for="ajuste in activados" :key="ajuste.id">
            <v-icon nombre="check" :tamano="20" />
            {{ ajuste.resumen }}
          </li>
        </ul>
        <p v-else :class="`${PREFIX}__secundario`">
          Nada por ahora: FROBI se ve como siempre. Lo puedes cambiar en Ajustes.
        </p>
      </section>
      <v-chip v-if="perfil.configuradoPor === 'acompanante'" icono="users" :class="`${PREFIX}__acompanante`">
        Configurado con ayuda de otra persona
      </v-chip>
      <div :class="`${PREFIX}__acciones`">
        <v-button variante="secundario" @click="ir(2)">Cambiar algo</v-button>
        <v-button :deshabilitado="guardando" @click="terminar">Empezar a aprender</v-button>
      </div>
    </template>
  </cmp-layout-asistente>
</template>

<script src="./cmp-asistente.ts" lang="ts"></script>

<style src="./cmp-asistente.scss" lang="scss" scoped></style>
