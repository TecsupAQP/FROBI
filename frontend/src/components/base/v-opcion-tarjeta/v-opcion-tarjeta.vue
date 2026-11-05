<template>
  <div :class="[PREFIX, `${PREFIX}--${disposicion}`, { [`${PREFIX}--elegida`]: elegida }]">
    <label :class="`${PREFIX}__etiqueta`">
      <input
        :class="`${PREFIX}__control`"
        :type="multiple ? 'checkbox' : 'radio'"
        :name="nombre"
        :checked="elegida"
        @change="$emit('elegir')"
      />
      <span :class="`${PREFIX}__cabecera`">
        <span v-if="icono" :class="`${PREFIX}__icono`" aria-hidden="true">
          <v-icon :nombre="icono" :tamano="disposicion === 'compacta' ? 32 : 30" />
        </span>
        <span v-if="disposicion !== 'compacta'" :class="`${PREFIX}__titulo`">{{ titulo }}</span>
        <v-icon v-if="elegida" :class="`${PREFIX}__check`" nombre="check" :tamano="24" />
      </span>
      <span v-if="disposicion === 'compacta'" :class="`${PREFIX}__titulo`">{{ titulo }}</span>
      <span v-if="descripcion" :class="`${PREFIX}__descripcion`">{{ descripcion }}</span>
    </label>
    <!-- Contenido extra (p. ej. el campo de código de clase) fuera de la label: no se anidan controles. -->
    <slot />
  </div>
</template>

<script src="./v-opcion-tarjeta.ts" lang="ts"></script>

<style src="./v-opcion-tarjeta.scss" lang="scss" scoped></style>
