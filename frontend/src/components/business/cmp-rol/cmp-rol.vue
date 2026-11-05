<template>
  <div :class="PREFIX">
    <v-chip :tono="perfil.modo === 'docente' ? 'marino' : 'marca'" :class="`${PREFIX}__paso`">
      Paso 1 · {{ NOMBRE_MODO[perfil.modo ?? "autonomo"] }}
    </v-chip>
    <cmp-encabezado-pagina
      titulo="¿Cómo vas a usar FROBI?"
      descripcion="Elige una opción. Puedes cambiarla después."
    />

    <form :class="`${PREFIX}__formulario`" novalidate @submit.prevent="continuar">
      <div :class="`${PREFIX}__opciones`" role="radiogroup" aria-label="Cómo vas a usar FROBI">
        <v-opcion-tarjeta
          nombre="modo"
          titulo="Soy docente"
          descripcion="Creo una clase, invito a mis alumnos y veo cómo avanzan."
          icono="users"
          :elegida="perfil.modo === 'docente'"
          @elegir="elegirModo('docente')"
        />
        <v-opcion-tarjeta
          nombre="modo"
          titulo="Soy estudiante con clase"
          descripcion="Mi docente me dio un código de clase."
          icono="book"
          :elegida="perfil.modo === 'estudiante-clase'"
          @elegir="elegirModo('estudiante-clase')"
        >
          <v-field
            id="rol-codigo"
            v-model="codigo"
            :class="`${PREFIX}__codigo`"
            etiqueta="Código de clase"
            placeholder="Ej. ABC123"
            autocompletar="off"
            :error="errorCodigo"
            :ayuda="claseEncontrada ? `Clase: ${claseEncontrada}` : undefined"
            @focusin="elegirModo('estudiante-clase')"
          />
        </v-opcion-tarjeta>
        <v-opcion-tarjeta
          nombre="modo"
          titulo="Aprendo por mi cuenta"
          descripcion="Practico a usar la IA con mis propios materiales."
          icono="spark"
          :elegida="perfil.modo === 'autonomo'"
          @elegir="elegirModo('autonomo')"
        />
      </div>

      <p :class="`${PREFIX}__privacidad`">
        <v-icon nombre="lock" :tamano="20" />
        Si te unes a una clase, tu docente ve tu actividad dentro de esa clase. Siempre te lo avisamos.
      </p>

      <v-button tipo="submit" :class="`${PREFIX}__continuar`" :deshabilitado="!perfil.modo || ocupado">
        {{ ocupado ? "Revisando…" : TEXTO_CONTINUAR[perfil.modo ?? "autonomo"] }}
      </v-button>
    </form>
  </div>
</template>

<script src="./cmp-rol.ts" lang="ts"></script>

<style src="./cmp-rol.scss" lang="scss" scoped></style>
