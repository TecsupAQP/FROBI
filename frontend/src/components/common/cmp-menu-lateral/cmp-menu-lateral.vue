<template>
  <Teleport to="body">
    <div v-if="abierto" :class="PREFIX" @click.self="cerrar" @keydown="alPresionar">
      <nav
        id="menu-lateral"
        ref="panel"
        :class="`${PREFIX}__panel`"
        role="dialog"
        aria-modal="true"
        aria-labelledby="menu-lateral-titulo"
        tabindex="-1"
      >
        <div :class="`${PREFIX}__cabecera`">
          <h2 id="menu-lateral-titulo" :class="`${PREFIX}__titulo`">Menú</h2>
          <button type="button" :class="`${PREFIX}__cerrar`" aria-label="Cerrar el menú" @click="cerrar">
            <v-icon nombre="x" :tamano="24" />
          </button>
        </div>
        <p v-if="estudiante" :class="`${PREFIX}__persona`">
          {{ estudiante.alias }} · {{ estudiante.rol === "docente" ? "Docente" : "Estudiante" }}
        </p>

        <section v-for="grupo in grupos" :key="grupo.titulo" :class="`${PREFIX}__grupo`">
          <h3 :class="`${PREFIX}__grupo-titulo`">{{ grupo.titulo }}</h3>
          <ul :class="`${PREFIX}__enlaces`">
            <li v-for="item in grupo.enlaces" :key="item.nombre">
              <router-link
                :to="item.destino"
                :class="[`${PREFIX}__enlace`, { [`${PREFIX}__enlace--actual`]: route.name === item.ruta }]"
                :aria-current="route.name === item.ruta ? 'page' : undefined"
                @click="cerrar"
              >
                <v-icon :nombre="item.icono" :tamano="22" />
                {{ item.nombre }}
              </router-link>
            </li>
          </ul>
        </section>

        <button type="button" :class="`${PREFIX}__enlace`" @click="verRecorrido">
          <v-icon nombre="map" :tamano="22" />
          Recorrido guiado
        </button>

        <button type="button" :class="`${PREFIX}__salir`" @click="salir">
          <v-icon nombre="back" :tamano="22" />
          Cerrar sesión
        </button>
      </nav>
    </div>
  </Teleport>
</template>

<script src="./cmp-menu-lateral.ts" lang="ts"></script>

<style src="./cmp-menu-lateral.scss" lang="scss" scoped></style>
