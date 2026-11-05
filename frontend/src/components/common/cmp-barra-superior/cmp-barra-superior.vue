<template>
  <header :class="PREFIX">
    <div :class="`${PREFIX}__contenido`">
      <router-link
        :class="`${PREFIX}__logo`"
        :to="{ name: RutaEnum.INICIO }"
        aria-label="FROBI, ir al inicio"
      >
        <v-logo :class="`${PREFIX}__logo-movil`" variante="icono" :alto="36" />
        <v-logo :class="`${PREFIX}__logo-escritorio`" :alto="40" />
      </router-link>
      <nav :class="`${PREFIX}__nav`" aria-label="Principal">
        <ul :class="`${PREFIX}__pestanas`">
          <li v-for="pestana in pestanas" :key="pestana.nombre">
            <router-link
              :to="{ name: pestana.ruta }"
              :class="[`${PREFIX}__pestana`, { [`${PREFIX}__pestana--activa`]: pestana.activa }]"
              :aria-current="pestana.activa ? 'page' : undefined"
            >
              <span :class="`${PREFIX}__pestana-corta`" aria-hidden="true">{{ pestana.nombreCorto }}</span>
              <span :class="`${PREFIX}__pestana-larga`">{{ pestana.nombre }}</span>
            </router-link>
          </li>
        </ul>
      </nav>
      <!-- Menú con todas las pantallas (la barra solo tiene 3 pestañas). -->
      <button
        v-if="estudiante"
        type="button"
        data-recorrido="menu"
        :class="`${PREFIX}__menu`"
        aria-haspopup="dialog"
        aria-controls="menu-lateral"
        :aria-expanded="menuAbierto"
        @click="menuAbierto = true"
      >
        <v-icon nombre="menu" :tamano="24" />
        <span :class="`${PREFIX}__menu-texto`">Menú</span>
      </button>
      <!-- El alias lleva a Ajustes (Mi cuenta). -->
      <router-link
        v-if="estudiante"
        :class="`${PREFIX}__alias`"
        :to="{ name: RutaEnum.AJUSTES }"
        :aria-label="`${estudiante.alias}, abrir ajustes`"
      >
        <span :class="`${PREFIX}__avatar`" aria-hidden="true">{{ inicial }}</span>
        <span :class="`${PREFIX}__alias-texto`">{{ estudiante.alias }}</span>
      </router-link>
    </div>
    <cmp-menu-lateral v-model="menuAbierto" />
  </header>
</template>

<script src="./cmp-barra-superior.ts" lang="ts"></script>

<style src="./cmp-barra-superior.scss" lang="scss" scoped></style>
