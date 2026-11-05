<template>
  <section :class="PREFIX" aria-labelledby="cmp-chat-titulo">
    <header :class="`${PREFIX}__encabezado`">
      <div :class="`${PREFIX}__identidad`">
        <span :class="`${PREFIX}__avatar`" aria-hidden="true">
          <img :src="logoIcono" alt="" width="30" height="30" />
          <span :class="[`${PREFIX}__punto`, `${PREFIX}__punto--${estadoVisible.clave}`]"></span>
        </span>
        <div>
          <h1 id="cmp-chat-titulo" :class="`${PREFIX}__titulo`">Pregúntale a FROBI</h1>
          <p :class="`${PREFIX}__estado`" role="status">{{ estadoVisible.texto }}</p>
        </div>
      </div>
      <button
        v-if="lineas.length"
        type="button"
        :class="`${PREFIX}__nueva`"
        :disabled="respondiendo"
        @click="nuevaConversacion"
      >
        <v-icon nombre="fwd" :tamano="20" />
        <span>Nueva conversación</span>
      </button>
    </header>

    <div ref="desplazable" :class="`${PREFIX}__mensajes`">
      <div v-if="!lineas.length" :class="`${PREFIX}__bienvenida`">
        <span :class="`${PREFIX}__mascota`" aria-hidden="true">
          <img :src="logoIcono" alt="" width="56" height="56" />
          <i :class="`${PREFIX}__chispa ${PREFIX}__chispa--1`"></i>
          <i :class="`${PREFIX}__chispa ${PREFIX}__chispa--2`"></i>
          <i :class="`${PREFIX}__chispa ${PREFIX}__chispa--3`"></i>
        </span>
        <h2 :class="`${PREFIX}__saludo`">¡Hola{{ alias ? `, ${alias}` : "" }}! Soy FROBI.</h2>
        <p :class="`${PREFIX}__presentacion`">{{ presentacion }}</p>
        <ul :class="`${PREFIX}__sugerencias`" aria-label="Preguntas para empezar">
          <li v-for="(sugerencia, indice) in sugerencias" :key="sugerencia.pregunta">
            <button
              type="button"
              :class="`${PREFIX}__sugerencia`"
              :style="{ animationDelay: `${120 + indice * 70}ms` }"
              :disabled="conexion !== 'en-linea'"
              @click="preguntar(sugerencia.pregunta)"
            >
              <span :class="`${PREFIX}__sugerencia-icono`" aria-hidden="true">
                <v-icon :nombre="sugerencia.icono" :tamano="22" />
              </span>
              <span :class="`${PREFIX}__sugerencia-texto`">
                <strong>{{ sugerencia.titulo }}</strong>
                {{ sugerencia.pregunta }}
              </span>
            </button>
          </li>
        </ul>
      </div>

      <ol
        v-else
        :class="`${PREFIX}__lista`"
        role="log"
        aria-live="polite"
        aria-label="Conversación con FROBI"
      >
        <cmp-mensaje-chat v-for="linea in lineas" :key="linea.id" :linea="linea" />
        <cmp-escribiendo v-if="esperandoTexto" :estado="consultando" />
      </ol>
    </div>

    <form :class="`${PREFIX}__redactor`" @submit.prevent="enviarBorrador">
      <v-aviso v-if="error" tipo="error">{{ error }}</v-aviso>
      <v-aviso v-else-if="!habilitado" tipo="nota">
        La IA no está activa en este momento: te respondo con ayuda básica sobre FROBI.
      </v-aviso>
      <div :class="[`${PREFIX}__campo`, { [`${PREFIX}__campo--activo`]: texto.trim() }]">
        <label for="cmp-chat-pregunta" class="solo-lector">Escribe tu pregunta para FROBI</label>
        <textarea
          id="cmp-chat-pregunta"
          ref="campo"
          v-model="texto"
          rows="1"
          :maxlength="MAX_CARACTERES"
          :placeholder="placeholder"
          :class="`${PREFIX}__texto`"
          @input="ajustarAltura"
          @keydown.enter.exact.prevent="enviarBorrador"
        ></textarea>
        <button
          type="submit"
          :class="`${PREFIX}__enviar`"
          :disabled="!puedeEnviar"
          aria-label="Enviar pregunta"
        >
          <v-icon nombre="arrow" :tamano="22" />
        </button>
      </div>
      <p :class="`${PREFIX}__pie`">
        <span>FROBI puede equivocarse: compara con tu material.</span>
        <span v-if="preguntasRestantes !== null && preguntasRestantes <= 10">
          Te quedan {{ preguntasRestantes }} preguntas en esta conversación.
        </span>
      </p>
    </form>
  </section>
</template>

<script src="./cmp-chat.ts" lang="ts"></script>

<style src="./cmp-chat.scss" lang="scss" scoped></style>
