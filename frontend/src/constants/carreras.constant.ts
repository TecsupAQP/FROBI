import type { Carrera } from "@/core/shared/domain/view/student.view";

// Carreras que se ofrecen al entrar. La API guarda el nombre tal cual.
export const CARRERAS: Carrera[] = [
  { id: "mecatronica", nombre: "Mecatrónica" },
  { id: "electronica", nombre: "Electrónica" },
  { id: "diseno-industrial", nombre: "Diseño industrial" },
  { id: "mantenimiento", nombre: "Mantenimiento" },
  { id: "otra", nombre: "Otra carrera" },
];
