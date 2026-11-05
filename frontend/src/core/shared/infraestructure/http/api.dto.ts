// Contrato de la API de FROBI (backend/openapi.json). Solo lo que consume el front.
export type RolApi = "learner" | "teacher";
export type FormatoApi = "visual_map" | "real_example" | "easy_read" | "audio";
export type PerfilApi = "low_vision" | "reading" | "hearing" | "attention" | "motor";
export type AjusteApi =
  | "voice"
  | "high_contrast"
  | "large_text"
  | "short_texts"
  | "captions"
  | "large_buttons"
  | "keyboard_mode";
export type EscalonApi = "hint_1" | "hint_2" | "step_by_step" | "final";
export type PiezaApi = "context" | "goal" | "level" | "format";
export type EstadoAfirmacionApi = "supported" | "unverifiable" | "contradicts";

export interface PersonaDto {
  id: string;
  alias: string;
  career: string;
  role: RolApi;
  configured_by: "self" | "companion";
}

export interface MembresiaDto {
  class_id: string;
  class_name: string;
  status: "joined";
}

export interface SesionDto {
  token: string;
  person: PersonaDto;
  membership: MembresiaDto | null;
}

export interface YoDto {
  person: PersonaDto;
  membership: MembresiaDto | null;
  onboarding: { done: boolean; intro_status: "seen" | "skipped" | "pending" };
}

export interface OnboardingDto {
  done: boolean;
  configured_by: "self" | "companion" | null;
  profiles: PerfilApi[];
  enabled_settings: AjusteApi[];
  intro_status: "seen" | "skipped" | "pending";
}

export interface AjustesDto extends Record<Exclude<AjusteApi, never>, boolean> {
  profiles: string[];
  language: "es" | "qu" | "ay";
}

export interface IdiomaDto {
  code: "es" | "qu" | "ay";
  name: string;
  status: "available" | "coming_soon";
}

export interface MaterialDto {
  id: string;
  title: string;
  kind: "guide" | "brief" | "draft" | "class_content";
  source: "sample" | "upload" | "paste";
  class_id: string | null;
  extracted_text: string;
  created_at: string;
  // Hay un PDF original guardado (vista previa con GET /materials/{id}/file).
  has_file?: boolean;
}

export interface MaterialArchivoDto {
  url: string;
  expires_in: number;
}

export interface MaterialResumenDto {
  id: string;
  title: string;
  kind: MaterialDto["kind"];
  source: MaterialDto["source"];
  preview: string;
}

export interface SeccionContenidoDto {
  heading: string;
  body: string;
  items: string[];
}

export interface RecetaDto {
  context: string;
  goal: string;
  level: string;
  format: FormatoApi;
}

export interface AdaptacionDto {
  id: string;
  material_id: string;
  format: FormatoApi;
  content: { title: string; sections: SeccionContenidoDto[]; plain_text: string };
  recipe: RecetaDto;
  prompt_text: string;
  ai_notice: string;
  fallback: boolean;
  created_at: string;
}

export interface IntentoAyudaDto {
  id: string;
  adaptation_id: string;
  task_ref: string;
  max_step: "none" | EscalonApi;
  next_step: EscalonApi | null;
  final_unlocked: boolean;
  own_answer_submitted: boolean;
  solved_without_ai: boolean;
  help_level: number;
  help_label: string;
}

export interface EscalonDto {
  attempt: IntentoAyudaDto;
  step: EscalonApi;
  content: string;
  fallback: boolean;
}

export interface RespuestaPropiaDto {
  attempt: IntentoAyudaDto;
  matching_passages: { text: string; location: string }[];
}

export interface PreguntaDto {
  id: string;
  adaptation_id: string;
  kind: "comprehension" | "transfer";
  statement: string;
  options: { id: string; text: string }[];
}

export interface RespuestaPreguntaDto {
  question_id: string;
  chosen_option: string;
  is_correct: boolean;
  correct_option: string;
  feedback: string;
  suggested_format: FormatoApi | null;
  used_help: boolean;
}

export interface EvaluacionInstruccionDto {
  id: string;
  text: string;
  scores: { piece: PiezaApi; score: number; feedback: string }[];
  missing_piece: PiezaApi | null;
  suggestion: string;
  improved_text: string;
  autonomy_level: number;
  autonomy_label: string;
}

export interface ComparacionInstruccionDto {
  evaluation_id: string;
  original: { prompt: string; output: string };
  improved: { prompt: string; output: string };
  fallback: boolean;
}

export interface TrabajoDto {
  id: string;
  brief_material_id: string;
  draft_material_id: string;
  organized: { requirements: string[]; topics: string[]; missing: string[] };
}

export interface AfirmacionDto {
  id: string;
  fragment: string;
  status: EstadoAfirmacionApi;
  reason: string;
  backing_passage: string | null;
  no_backing_message: string | null;
}

export interface RevisionDto {
  work_id: string;
  sections: { section: string; claims: AfirmacionDto[] }[];
}

export interface HerramientaDto {
  id: string;
  name: string;
  need: string;
  use_for: string;
  avoid_for: string;
}

export interface RecomendacionDto {
  tool: HerramientaDto;
  why: string;
  when_not: string;
}

export interface ProgresoDto {
  has_data: boolean;
  formats_used: { format: FormatoApi; count: number }[];
  accuracy_by_format: { format: FormatoApi; correct: number; total: number }[];
  prompt_scores: { at: string; total: number }[];
  solved_without_ai: number;
  message: string;
}

export interface CierreDto {
  favorite_format: FormatoApi | null;
  learned_recipe: RecetaDto | null;
  best_prompt_score: number | null;
  autonomy_level: number | null;
  message: string;
}

export interface ClaseDto {
  id: string;
  name: string;
  subject: string;
  tasks: string[];
  invite_code: string;
  created_at: string;
}

export interface MiembroDto {
  alias: string;
  person_id: string | null;
  status: "invited" | "joined" | "left";
  status_label: string;
  joined_at: string | null;
}

export interface MiembrosDto {
  invite_code: string;
  members: MiembroDto[];
}

export interface PanelDto {
  class_id: string;
  sample_data: boolean;
  students: {
    person_id: string;
    alias: string;
    progress_label: string;
    alerts: { code: string; text: string; icon: string }[];
  }[];
  top_formats: { format: FormatoApi; count: number }[];
  most_failed_questions: { statement: string; fail_rate: number }[];
  ai_usage: { help_requests: number; solved_without_ai: number };
}

export interface DetalleEstudianteDto {
  person_id: string;
  alias: string;
  preferred_format: FormatoApi | null;
  correct_answers: number;
  total_answers: number;
  help_by_step: { step: EscalonApi; count: number }[];
  solved_without_ai: number;
  most_failed_question: string | null;
}
