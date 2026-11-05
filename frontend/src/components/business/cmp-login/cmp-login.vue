<template>
  <div :class="PREFIX">
    <cmp-panel-marca :class="`${PREFIX}__marca`" />

    <main id="contenido" :class="`${PREFIX}__acceso`" tabindex="-1">
      <div :class="`${PREFIX}__bienvenida`">
        <v-logo :alto="48" />
        <h1 :class="`${PREFIX}__lema`">Aprende con IA, aprende a usar IA.</h1>
        <p :class="`${PREFIX}__descripcion`">Convierte tu guía de clase en el formato que necesitas.</p>
      </div>

      <form
        :class="`${PREFIX}__tarjeta`"
        novalidate
        aria-labelledby="cmp-login-titulo"
        @submit.prevent="enviar"
      >
        <div :class="`${PREFIX}__titulos`">
          <h2 id="cmp-login-titulo" :class="`${PREFIX}__titulo`">Entra con tu alias</h2>
          <p :class="`${PREFIX}__subtitulo`">No pedimos correo ni contraseña.</p>
        </div>

        <v-field
          id="login-alias"
          v-model="alias"
          etiqueta="Tu alias"
          placeholder="Ej. mecatronico_01"
          autocompletar="nickname"
          :error="errores.alias"
        />

        <v-select
          id="login-carrera"
          v-model="carrera"
          etiqueta="Tu carrera"
          :opciones="carreras"
          :error="errores.carrera"
        />

        <fieldset :class="`${PREFIX}__rol`">
          <legend :class="`${PREFIX}__leyenda`">Tu rol</legend>
          <div :class="`${PREFIX}__roles`">
            <v-radio-opcion
              v-for="opcion in ROLES"
              :key="opcion.valor"
              v-model="rol"
              nombre="rol"
              :valor="opcion.valor"
              :error="Boolean(errores.rol)"
              :descripcion="errores.rol ? 'login-rol-error' : undefined"
            >
              {{ opcion.nombre }}
            </v-radio-opcion>
          </div>
          <p v-if="errores.rol" id="login-rol-error" :class="`${PREFIX}__error`">
            <v-icon nombre="alert" :tamano="20" />
            {{ errores.rol }}
          </p>
        </fieldset>

        <v-field
          id="login-codigo"
          v-model="codigoClase"
          etiqueta="Código de clase (opcional)"
          placeholder="Ejemplo: SENS-4821"
          autocompletar="off"
          :error="errores.codigo"
          ayuda="Si tu docente te dio un código, escríbelo aquí."
        />

        <v-button tipo="submit" bloque :icono-fin="enviando ? undefined : 'arrow'" :deshabilitado="enviando">
          {{ enviando ? "Entrando…" : "Entrar" }}
        </v-button>

        <p :class="`${PREFIX}__privacidad`">Tu material no se usa para otros fines.</p>
      </form>
    </main>
  </div>
</template>

<script src="./cmp-login.ts" lang="ts"></script>

<style src="./cmp-login.scss" lang="scss" scoped></style>
