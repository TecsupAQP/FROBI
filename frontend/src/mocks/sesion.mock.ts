import type { Carrera, Student } from "@/core/shared/domain/view/student.view";

export const ESTUDIANTE_DEMO: Student = {
  alias: "mecatronico_01",
  carrera: "mecatronica",
  rol: "estudiante",
};

export const CARRERAS_MOCK: Carrera[] = [
  { id: "mecatronica", nombre: "Mecatrónica" },
  { id: "electronica", nombre: "Electrónica" },
  { id: "diseno-industrial", nombre: "Diseño industrial" },
  { id: "mantenimiento", nombre: "Mantenimiento" },
  { id: "otra", nombre: "Otra carrera" },
];
