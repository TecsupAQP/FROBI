<template>
  <div :class="PREFIX">
    <header :class="`${PREFIX}__encabezado`">
      <h1 :class="`${PREFIX}__titulo`">Un mismo sistema, distintas personas</h1>
      <p :class="`${PREFIX}__descripcion`">
        La escalera de ayuda se adapta a cada perfil. Las personas y los casos son inventados: aún no están
        validados con usuarios reales.
      </p>
    </header>

    <ul :class="`${PREFIX}__lista`">
      <li
        v-for="persona in PERSONAS_MOCK"
        :key="persona.id"
        :class="[`${PREFIX}__persona`, { [`${PREFIX}__persona--ancha`]: ANCHAS.includes(persona.id) }]"
      >
        <p :class="`${PREFIX}__perfil`">
          <v-icon :nombre="persona.icono" :tamano="22" />
          {{ persona.perfil }}
        </p>
        <div>
          <h2 :class="`${PREFIX}__nombre`">{{ persona.nombre }}</h2>
          <p :class="`${PREFIX}__situacion`">{{ persona.situacion }}</p>
        </div>

        <!-- Vista en miniatura de cómo se ve la escalera para esta persona (no es interactiva). -->
        <div :class="[`${PREFIX}__pantalla`, `${PREFIX}__pantalla--${persona.pantalla}`]" aria-hidden="true">
          <template v-if="persona.pantalla === 'voz'">
            <p :class="`${PREFIX}__mini-etiqueta`">Pista 1 de 4</p>
            <p :class="`${PREFIX}__mini-titulo`">Revisa en tu guía qué material detecta cada sensor.</p>
            <span :class="`${PREFIX}__mini-chip ${PREFIX}__mini-chip--voz`">
              <v-icon nombre="headphones" :tamano="20" />
              Escuchar este paso
            </span>
          </template>
          <template v-else-if="persona.pantalla === 'pasos'">
            <p :class="`${PREFIX}__mini-etiqueta`">Paso 1 de 4</p>
            <p :class="`${PREFIX}__mini-titulo`">Lee una frase.</p>
            <span :class="`${PREFIX}__mini-boton`">Siguiente</span>
          </template>
          <template v-else-if="persona.pantalla === 'transcripcion'">
            <p :class="`${PREFIX}__mini-etiqueta ${PREFIX}__mini-etiqueta--marca`">Transcripción</p>
            <p>«Revisa en tu guía qué material detecta cada sensor.»</p>
            <span :class="`${PREFIX}__mini-chip`">
              <v-icon nombre="captions" :tamano="20" />
              Sin sonido obligatorio
            </span>
          </template>
          <template v-else-if="persona.pantalla === 'teclado'">
            <span :class="`${PREFIX}__mini-boton ${PREFIX}__mini-boton--grande`">Siguiente pista</span>
            <p :class="`${PREFIX}__mini-nota`">Atajo de teclado: Enter</p>
          </template>
          <template v-else>
            <span :class="`${PREFIX}__mini-chip ${PREFIX}__mini-chip--exito`">
              <v-icon nombre="users" :tamano="20" />
              Ahora · Lucía configura
            </span>
            <span :class="`${PREFIX}__mini-chip`">
              <v-icon nombre="check" :tamano="20" />
              Después · Don Pedro aprende solo
            </span>
          </template>
        </div>

        <div :class="`${PREFIX}__cambios`">
          <h3 :class="`${PREFIX}__cambios-titulo`">Qué cambia</h3>
          <ul :class="`${PREFIX}__cambios-lista`">
            <li v-for="cambio in persona.cambios" :key="cambio">
              <v-icon nombre="check" :tamano="20" />
              {{ cambio }}
            </li>
          </ul>
        </div>

        <p :class="`${PREFIX}__ayuda`">
          <v-icon nombre="users" :tamano="20" />
          Quién ayuda: {{ persona.quienAyuda }}
        </p>
      </li>
    </ul>
  </div>
</template>

<script src="./cmp-personas.ts" lang="ts"></script>

<style src="./cmp-personas.scss" lang="scss" scoped></style>
