<template>
  <div :class="PREFIX">
    <section :class="`${PREFIX}__frases`" :aria-labelledby="`${PREFIX}-frases`">
      <h3 :id="`${PREFIX}-frases`" :class="`${PREFIX}__titulo`">Frases cortas</h3>
      <ul :class="`${PREFIX}__lista`">
        <li v-for="frase in contenido.frases" :key="frase" :class="`${PREFIX}__frase`">{{ frase }}</li>
      </ul>
    </section>
    <section
      v-if="contenido.glosario.length"
      :class="`${PREFIX}__glosario`"
      :aria-labelledby="`${PREFIX}-glosario`"
    >
      <h3 :id="`${PREFIX}-glosario`" :class="`${PREFIX}__titulo`">Glosario</h3>
      <dl :class="`${PREFIX}__terminos`">
        <div v-for="item in contenido.glosario" :key="item.termino">
          <dt :class="`${PREFIX}__termino`">{{ item.termino }}</dt>
          <dd :class="`${PREFIX}__definicion`">{{ item.definicion }}</dd>
        </div>
      </dl>
    </section>
  </div>
</template>

<script src="./cmp-lectura-facil.ts" lang="ts"></script>

<style src="./cmp-lectura-facil.scss" lang="scss" scoped></style>
