<template>
  <component
    :is="destino ? RouterLink : 'button'"
    :class="[PREFIX, `${PREFIX}--${variante}`, { [`${PREFIX}--bloque`]: bloque }]"
    :to="destino"
    :type="destino ? undefined : tipo"
    :disabled="destino ? undefined : deshabilitado"
    :aria-disabled="deshabilitado || undefined"
    :aria-label="variante === 'cerrar' ? (etiqueta ?? 'Cerrar') : etiqueta"
    @click="$emit('click', $event)"
  >
    <v-icon v-if="variante === 'cerrar'" nombre="x" />
    <template v-else>
      <v-icon v-if="icono" :nombre="icono" />
      <span :class="`${PREFIX}__texto`"><slot /></span>
      <v-icon v-if="iconoFin" :nombre="iconoFin" />
    </template>
  </component>
</template>

<script src="./v-button.ts" lang="ts"></script>

<style src="./v-button.scss" lang="scss" scoped></style>
