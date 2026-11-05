<template>
  <div :class="PREFIX">
    <div :class="`${PREFIX}__reproductor`">
      <div>
        <p :class="`${PREFIX}__titulo`">{{ contenido.titulo }}</p>
        <p :class="`${PREFIX}__detalle`">
          {{ contenido.voz }} · {{ formatearTiempo(contenido.duracionSegundos) }}
        </p>
      </div>
      <div :class="`${PREFIX}__progreso`">
        <v-progress-bar
          :valor="posicion"
          :maximo="contenido.duracionSegundos"
          etiqueta="Avance del audio"
          :texto-valor="`${formatearTiempo(posicion)} de ${formatearTiempo(contenido.duracionSegundos)}`"
          tono="claro"
        />
        <p :class="`${PREFIX}__tiempos`" aria-hidden="true">
          <span>{{ formatearTiempo(posicion) }}</span>
          <span>{{ formatearTiempo(contenido.duracionSegundos) }}</span>
        </p>
      </div>
      <div :class="`${PREFIX}__controles`">
        <button
          type="button"
          :class="`${PREFIX}__control`"
          aria-label="Retroceder 10 segundos"
          @click="mover(-10)"
        >
          <v-icon nombre="back" :tamano="20" />
          10 s
        </button>
        <button
          type="button"
          :class="`${PREFIX}__reproducir`"
          :aria-label="reproduciendo ? 'Pausar' : 'Reproducir'"
          :aria-pressed="reproduciendo"
          @click="alternar"
        >
          <v-icon v-if="reproduciendo" nombre="pause" :tamano="30" />
          <v-icon v-else nombre="play" :tamano="30" />
        </button>
        <button
          type="button"
          :class="`${PREFIX}__control`"
          aria-label="Adelantar 10 segundos"
          @click="mover(10)"
        >
          <v-icon nombre="fwd" :tamano="20" />
          10 s
        </button>
        <button
          type="button"
          :class="`${PREFIX}__control`"
          :aria-label="`Velocidad ${velocidad} por uno, cambiar`"
          @click="cambiarVelocidad"
        >
          {{ velocidad }}×
        </button>
      </div>
    </div>

    <p v-if="!vozDisponible" :class="`${PREFIX}__aviso`" role="status">
      Tu navegador no tiene voz. Puedes leer el texto aquí abajo.
    </p>

    <section :class="`${PREFIX}__texto`" :aria-labelledby="`${PREFIX}-texto`">
      <h3 :id="`${PREFIX}-texto`" :class="`${PREFIX}__subtitulo`">Lo que escuchas</h3>
      <p
        v-for="(frase, indice) in contenido.frases"
        :key="frase"
        :class="[`${PREFIX}__frase`, { [`${PREFIX}__frase--actual`]: indice === fraseActual }]"
        :aria-current="indice === fraseActual ? 'true' : undefined"
      >
        {{ frase }}
      </p>
    </section>
  </div>
</template>

<script src="./cmp-audio.ts" lang="ts"></script>

<style src="./cmp-audio.scss" lang="scss" scoped></style>
