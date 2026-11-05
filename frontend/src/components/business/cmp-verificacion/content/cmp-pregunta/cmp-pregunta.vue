<template>
  <section :class="PREFIX" :aria-labelledby="`${PREFIX}-${pregunta.id}`">
    <h2 :id="`${PREFIX}-${pregunta.id}`" :class="`${PREFIX}__enunciado`">{{ pregunta.enunciado }}</h2>
    <ul :class="`${PREFIX}__opciones`" role="list">
      <li v-for="opcion in pregunta.opciones" :key="opcion.id">
        <button
          type="button"
          :class="[`${PREFIX}__opcion`, claseOpcion(opcion.id)]"
          :aria-pressed="opcion.id === elegida"
          :aria-disabled="bloqueada || undefined"
          @click="!bloqueada && $emit('responder', opcion.id)"
        >
          <span :class="`${PREFIX}__letra`" aria-hidden="true">{{ opcion.letra }}</span>
          <span :class="`${PREFIX}__texto`">{{ opcion.texto }}</span>
          <span v-if="opcion.id === elegida" :class="`${PREFIX}__veredicto`">
            <v-icon :nombre="acerto ? 'check' : 'x'" />
            {{ acerto ? "Correcta" : "Incorrecta" }}
          </span>
        </button>
      </li>
    </ul>

    <div :class="`${PREFIX}__vivo`" aria-live="polite">
      <div v-if="revisando" :class="`${PREFIX}__revisando`">
        <v-cargando>Revisando tu respuesta…</v-cargando>
      </div>
      <div
        v-else-if="respondida"
        :class="[`${PREFIX}__respuesta`, acerto ? `${PREFIX}__respuesta--bien` : `${PREFIX}__respuesta--mal`]"
      >
        <v-icon :nombre="acerto ? 'check' : 'x'" :tamano="26" />
        <div>
          <p :class="`${PREFIX}__respuesta-titulo`">{{ acerto ? "¡Muy bien!" : "Todavía no" }}</p>
          <p :class="`${PREFIX}__respuesta-texto`">
            {{ acerto ? pregunta.explicacionAcierto : pregunta.explicacionError }}
          </p>
        </div>
      </div>
    </div>

    <slot />
  </section>
</template>

<script src="./cmp-pregunta.ts" lang="ts"></script>

<style src="./cmp-pregunta.scss" lang="scss" scoped></style>
