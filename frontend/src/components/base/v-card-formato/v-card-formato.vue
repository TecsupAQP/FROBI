<template>
  <component
    :is="destino ? RouterLink : 'button'"
    :class="[PREFIX, { [`${PREFIX}--atenuada`]: atenuada, [`${PREFIX}--elegida`]: elegida }]"
    :to="destino"
    :type="destino ? undefined : 'button'"
    :disabled="destino ? undefined : atenuada"
    :aria-disabled="atenuada || undefined"
    :aria-pressed="destino ? undefined : elegida"
    @click="$emit('elegir', formato.id)"
  >
    <span :class="`${PREFIX}__icono`">
      <v-icon :nombre="formato.icono" :tamano="28" />
    </span>
    <span :class="`${PREFIX}__textos`">
      <span :class="`${PREFIX}__nombre`">{{ formato.nombre }}</span>
      <span :class="`${PREFIX}__descripcion`">{{ formato.descripcion }}</span>
    </span>
    <v-icon :class="`${PREFIX}__flecha`" nombre="chev" />
  </component>
</template>

<script src="./v-card-formato.ts" lang="ts"></script>

<style src="./v-card-formato.scss" lang="scss" scoped></style>
