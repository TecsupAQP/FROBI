<template>
  <nav :class="PREFIX" :aria-labelledby="`${PREFIX}-titulo`">
    <p :id="`${PREFIX}-titulo`" :class="`${PREFIX}__titulo`">Cambiar de formato</p>
    <ul :class="`${PREFIX}__opciones`">
      <li v-for="formato in FORMATOS" :key="formato.id">
        <router-link
          :to="{ name: RutaEnum.RESULTADO, params: { formato: formato.id }, query: $route.query }"
          :class="[`${PREFIX}__opcion`, { [`${PREFIX}__opcion--activa`]: formato.id === activo }]"
          :aria-current="formato.id === activo ? 'page' : undefined"
        >
          <v-icon :nombre="formato.icono" :tamano="20" />
          {{ formato.nombreCorto }}
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<script src="./cmp-selector-formato.ts" lang="ts"></script>

<style src="./cmp-selector-formato.scss" lang="scss" scoped></style>
