<template>
  <teleport to="body">
    <transition :name="PREFIX">
      <div v-if="abierto" :class="PREFIX" @mousedown.self="cerrar">
        <div
          ref="dialogo"
          :class="`${PREFIX}__dialogo`"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="`${id}-titulo`"
          :aria-describedby="descripcion ? `${id}-descripcion` : undefined"
          tabindex="-1"
          @keydown="alPresionar"
        >
          <header :class="`${PREFIX}__encabezado`">
            <div :class="`${PREFIX}__titulos`">
              <h2 :id="`${id}-titulo`" :class="`${PREFIX}__titulo`">{{ titulo }}</h2>
              <p v-if="descripcion" :id="`${id}-descripcion`" :class="`${PREFIX}__descripcion`">
                {{ descripcion }}
              </p>
            </div>
            <v-button variante="cerrar" etiqueta="Cerrar ventana" @click="cerrar" />
          </header>
          <div :class="`${PREFIX}__cuerpo`">
            <slot />
          </div>
          <footer v-if="$slots.pie" :class="`${PREFIX}__pie`">
            <slot name="pie" />
          </footer>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script src="./v-modal.ts" lang="ts"></script>

<style src="./v-modal.scss" lang="scss" scoped></style>
