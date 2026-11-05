<template>
  <Teleport to="body">
    <template v-if="activo && paso">
      <!-- Oscurece la pantalla salvo la parte resaltada; no bloquea los clics. -->
      <div v-if="marco" :class="`${PREFIX}__foco`" :style="estiloMarco" aria-hidden="true"></div>
      <div v-else :class="`${PREFIX}__velo`" aria-hidden="true"></div>

      <section :class="PREFIX" role="dialog" aria-modal="false" aria-labelledby="recorrido-titulo">
        <div :class="`${PREFIX}__cabecera`">
          <p :class="`${PREFIX}__antetitulo`">Recorrido guiado</p>
          <button type="button" :class="`${PREFIX}__cerrar`" aria-label="Salir del recorrido" @click="salir">
            <v-icon nombre="x" :tamano="24" />
          </button>
        </div>
        <v-pasos :actual="indice + 1" :total="pasos.length" />
        <h2 id="recorrido-titulo" ref="titulo" :class="`${PREFIX}__titulo`" tabindex="-1">
          {{ paso.titulo }}
        </h2>
        <p :class="`${PREFIX}__texto`" aria-live="polite">{{ paso.texto }}</p>
        <p v-if="falta && paso.siFalta" :class="`${PREFIX}__nota`">{{ paso.siFalta }}</p>
        <div :class="`${PREFIX}__acciones`">
          <v-button variante="texto" @click="salir">Saltar</v-button>
          <div :class="`${PREFIX}__navegacion`">
            <v-button v-if="!esPrimero" variante="secundario" @click="anterior"> Anterior </v-button>
            <v-button v-if="!esUltimo" @click="siguiente">Siguiente</v-button>
            <v-button v-else @click="salir">Terminar</v-button>
          </div>
        </div>
      </section>
    </template>
  </Teleport>
</template>

<script src="./cmp-recorrido.ts" lang="ts"></script>

<style src="./cmp-recorrido.scss" lang="scss" scoped></style>
