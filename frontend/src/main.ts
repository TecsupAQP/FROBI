import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "@/App.vue";
import router from "@/router";
import { ApiError } from "@/core/shared/infraestructure/http/api.client";
import { SinConexionError } from "@/core/shared/application/util/errores.util";
import { useCmpAvisosStore } from "@/store/common/cmp-avisos/cmp-avisos.store";
import "@/assets/styles/main.scss";

const app = createApp(App).use(createPinia()).use(router);

// Fallos de la API que ninguna pantalla manejó: se avisan en vez de dejar la pantalla cargando.
const avisarFallo = (error: unknown) => {
  const { mostrarAviso } = useCmpAvisosStore();
  if (error instanceof SinConexionError) {
    mostrarAviso("Sin conexión con FROBI", "Revisa tu internet y vuelve a intentarlo.");
  } else if (error instanceof ApiError && error.status !== 401) {
    mostrarAviso("Algo salió mal", error.detalle);
  } else if (!(error instanceof ApiError)) {
    console.error(error);
  }
};

app.config.errorHandler = avisarFallo;
window.addEventListener("unhandledrejection", (evento) => {
  if (evento.reason instanceof SinConexionError || evento.reason instanceof ApiError) {
    evento.preventDefault();
    avisarFallo(evento.reason);
  }
});

app.mount("#app");
