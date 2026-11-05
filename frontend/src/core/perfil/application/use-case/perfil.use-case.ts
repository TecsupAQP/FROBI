import type { PerfilPort } from "@/core/perfil/infraestructure/ports/in/perfil.port";
import type { AjusteId, Ajustes, Idioma } from "@/core/shared/domain/view/ajustes.view";
import type { ModoUso, Perfil, ResultadoCodigoClase } from "@/core/shared/domain/view/perfil.view";
import { api, esErrorApi } from "@/core/shared/infraestructure/http/api.client";
import type { AjustesDto, IdiomaDto, OnboardingDto, YoDto } from "@/core/shared/infraestructure/http/api.dto";
import { perfilesDesdeApi, perfilesHaciaApi } from "@/core/shared/infraestructure/http/api.mapper";
import { DETALLE_IDIOMA } from "@/constants/perfil.constant";

// Lo que la API no guarda (por qué puerta entró y el código que escribió) vive en el navegador.
const CLAVE_LOCAL = "frobi-perfil-local";

interface PerfilLocal {
  modo: ModoUso | null;
  codigoClase: string | null;
  vioIntro: boolean;
}

function leerLocal(): PerfilLocal {
  try {
    const guardado = localStorage.getItem(CLAVE_LOCAL);
    if (guardado) return JSON.parse(guardado) as PerfilLocal;
  } catch {
    // Sin almacenamiento: se usan los valores de la API.
  }
  return { modo: null, codigoClase: null, vioIntro: false };
}

function escribirLocal(perfil: Perfil): void {
  try {
    const local: PerfilLocal = {
      modo: perfil.modo,
      codigoClase: perfil.codigoClase,
      vioIntro: perfil.vioIntro,
    };
    localStorage.setItem(CLAVE_LOCAL, JSON.stringify(local));
  } catch {
    // Sin almacenamiento: estos datos viven solo en memoria.
  }
}

// Cada interruptor del front controla uno o dos ajustes de la API.
const AJUSTES: Record<AjusteId, (keyof AjustesDto)[]> = {
  voz: ["voice"],
  contraste: ["high_contrast", "large_text"],
  "textos-cortos": ["short_texts"],
  subtitulos: ["captions"],
  "botones-grandes": ["large_buttons", "keyboard_mode"],
};

// GET /me, POST /me/onboarding(/reset), GET y PATCH /me/settings, GET /languages, POST /classes/join.
export class PerfilUseCase implements PerfilPort {
  async obtenerPerfil(): Promise<Perfil> {
    const [yo, ajustes] = await Promise.all([api.get<YoDto>("/me"), api.get<AjustesDto>("/me/settings")]);
    const local = leerLocal();
    const modoPorDefecto: ModoUso | null =
      yo.person.role === "teacher" ? "docente" : yo.membership ? "estudiante-clase" : null;
    return {
      modo: local.modo ?? modoPorDefecto,
      codigoClase: local.codigoClase,
      perfiles: perfilesDesdeApi(ajustes.profiles),
      configuradoPor: yo.person.configured_by === "companion" ? "acompanante" : "yo",
      vioIntro: local.vioIntro || yo.onboarding.intro_status !== "pending",
      vioAsistente: yo.onboarding.done,
    };
  }

  async guardarPerfil(perfil: Perfil): Promise<Perfil> {
    escribirLocal(perfil);
    const yo = await api.get<YoDto>("/me");
    if (perfil.vioAsistente && !yo.onboarding.done) {
      // Completar el asistente aplica en la API los ajustes de cada perfil elegido.
      await api.post<OnboardingDto>("/me/onboarding", {
        who_uses: perfil.configuradoPor === "acompanante" ? "companion" : "self",
        profiles: perfilesHaciaApi(perfil.perfiles),
        intro: perfil.vioIntro ? "seen" : "skipped",
      });
    } else if (!perfil.vioAsistente && yo.onboarding.done) {
      await api.post<OnboardingDto>("/me/onboarding/reset");
    }
    return this.obtenerPerfil();
  }

  // Unirse a una clase con su código (POST /classes/join).
  async validarCodigoClase(codigo: string): Promise<ResultadoCodigoClase> {
    try {
      const union = await api.post<{ class_id: string; class_name: string }>("/classes/join", {
        code: codigo.trim(),
      });
      return { valido: true, claseId: union.class_id, nombreClase: union.class_name };
    } catch (error) {
      if (esErrorApi(error) && error.status === 422) {
        return { valido: false, mensaje: "No encontramos esa clase. Revisa el código con tu docente." };
      }
      throw error;
    }
  }

  async obtenerAjustes(): Promise<Ajustes> {
    return this.ajustesDesdeApi(await api.get<AjustesDto>("/me/settings"));
  }

  async guardarAjustes(ajustes: Ajustes): Promise<Ajustes> {
    const cambios: Partial<Record<keyof AjustesDto, boolean | string>> = { language: ajustes.idioma };
    (Object.keys(AJUSTES) as AjusteId[]).forEach((id) =>
      AJUSTES[id].forEach((clave) => (cambios[clave] = ajustes.activos[id])),
    );
    return this.ajustesDesdeApi(await api.patch<AjustesDto>("/me/settings", cambios));
  }

  async obtenerIdiomas(): Promise<Idioma[]> {
    const idiomas = await api.get<IdiomaDto[]>("/languages");
    return idiomas.map((idioma) => ({
      id: idioma.code,
      nombre: idioma.name,
      detalle: DETALLE_IDIOMA[idioma.code],
      disponible: idioma.status === "available",
    }));
  }

  private ajustesDesdeApi(dto: AjustesDto): Ajustes {
    const activos = {} as Ajustes["activos"];
    (Object.keys(AJUSTES) as AjusteId[]).forEach((id) => {
      activos[id] = AJUSTES[id].some((clave) => dto[clave] === true);
    });
    return { idioma: dto.language, activos };
  }
}
