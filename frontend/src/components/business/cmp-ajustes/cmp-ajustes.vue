<template>
  <div :class="PREFIX">
    <cmp-encabezado-pagina
      titulo="Ajustes"
      descripcion="Cambia cuando quieras lo que elegiste la primera vez."
    />

    <div :class="`${PREFIX}__columnas`">
      <div :class="`${PREFIX}__principal`">
        <section :class="`${PREFIX}__tarjeta`" aria-labelledby="ajustes-idioma">
          <h2 id="ajustes-idioma" :class="`${PREFIX}__titulo`">Idioma de la interfaz</h2>
          <ul :class="`${PREFIX}__idiomas`">
            <li
              v-for="idioma in idiomas"
              :key="idioma.id"
              :class="[
                `${PREFIX}__idioma`,
                {
                  [`${PREFIX}__idioma--elegido`]: idioma.id === ajustes.idioma,
                  [`${PREFIX}__idioma--pronto`]: !idioma.disponible,
                },
              ]"
              :aria-current="idioma.id === ajustes.idioma ? 'true' : undefined"
              :aria-disabled="!idioma.disponible || undefined"
            >
              <span :class="`${PREFIX}__idioma-textos`">
                <span :class="`${PREFIX}__idioma-nombre`">{{ idioma.nombre }}</span>
                <span v-if="idioma.detalle" :class="`${PREFIX}__idioma-detalle`">{{ idioma.detalle }}</span>
              </span>
              <v-icon v-if="idioma.id === ajustes.idioma" nombre="check" etiqueta="Elegido" />
              <v-chip v-else-if="!idioma.disponible" tono="neutro" icono="clock">Próximamente</v-chip>
            </li>
          </ul>
          <v-aviso tipo="nota">Cada idioma nuevo se agrega con revisión de personas que lo hablan.</v-aviso>
        </section>

        <section :class="`${PREFIX}__tarjeta`" aria-labelledby="ajustes-accesibilidad">
          <h2 id="ajustes-accesibilidad" :class="`${PREFIX}__titulo`">Accesibilidad</h2>
          <v-switch
            v-for="ajuste in AJUSTES_ACCESIBILIDAD"
            :id="`ajuste-${ajuste.id}`"
            :key="ajuste.id"
            :etiqueta="ajuste.nombre"
            :model-value="ajustes.activos[ajuste.id]"
            @update:model-value="cambiar(ajuste.id)"
          />
          <v-aviso v-if="ajustes.activos.voz && !disponible" tipo="aviso" role="status">
            Tu navegador no tiene lectura por voz. Activa «Ver el texto de lo que se dice» para leerlo en
            pantalla.
          </v-aviso>
          <v-button variante="secundario" bloque @click="rehacerAsistente"
            >Volver a hacer el asistente</v-button
          >
          <router-link :class="`${PREFIX}__enlace`" :to="{ name: RutaEnum.PERFIL_ACCESIBILIDAD }">
            Elegir según mi perfil de accesibilidad
          </router-link>
        </section>
      </div>

      <div :class="`${PREFIX}__lateral`">
        <section :class="`${PREFIX}__tarjeta`" aria-labelledby="ajustes-cuenta">
          <h2 id="ajustes-cuenta" :class="`${PREFIX}__titulo`">Mi cuenta</h2>
          <v-field
            id="ajustes-alias"
            v-model="alias"
            etiqueta="Tu alias"
            autocompletar="nickname"
            @change="guardarAlias"
          />
          <template v-if="estoyEnClase && clase">
            <v-chip :class="`${PREFIX}__clase`">Clase: {{ clase.nombre }}</v-chip>
            <v-button variante="secundario" bloque @click="salirDeClase">Salir de la clase</v-button>
          </template>
          <p v-else :class="`${PREFIX}__secundario`">No estás en ninguna clase. Aprendes por tu cuenta.</p>
          <v-button variante="texto" bloque icono="back" @click="salirDeFrobi">Cerrar sesión</v-button>
        </section>

        <section :class="`${PREFIX}__tarjeta`" aria-labelledby="ajustes-docente">
          <h2 id="ajustes-docente" :class="`${PREFIX}__titulo`">Qué ve tu docente</h2>
          <p :class="`${PREFIX}__privacidad`">
            <v-icon :class="`${PREFIX}__si`" nombre="check" :tamano="20" />
            Tu actividad dentro de la clase: ayudas usadas, ejercicios y avance.
          </p>
          <p :class="`${PREFIX}__privacidad`">
            <v-icon nombre="lock" :tamano="20" />
            No ve lo que haces fuera de la clase.
          </p>
        </section>
      </div>
    </div>
  </div>
</template>

<script src="./cmp-ajustes.ts" lang="ts"></script>

<style src="./cmp-ajustes.scss" lang="scss" scoped></style>
