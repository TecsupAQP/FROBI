import type { Clase, DetalleAlumno } from "@/core/shared/domain/view/clase.view";
import { CODIGO_CLASE_EJEMPLO } from "@/mocks/perfil.mock";

// Personas inventadas para la demo: se muestran siempre como datos de ejemplo.
export const CLASE_MOCK: Clase = {
  id: "clase-sensores",
  nombre: "Sensores industriales",
  carrera: "Mecatrónica",
  ciclo: "ciclo 1",
  codigo: CODIGO_CLASE_EJEMPLO,
  alumnos: [
    {
      alias: "ana",
      nombre: "Ana Condori",
      estado: "se-unio",
      avance: 66,
      posicion: "Pista 2 de 4 · tarea 1 de 3",
      nota: "Resolvió 2 ejercicios sin IA.",
      alerta: { tipo: "va-bien", texto: "Va bien" },
    },
    {
      alias: "luis",
      nombre: "Luis Mamani",
      estado: "invitado",
      avance: 25,
      posicion: "Pista 1 de 4 · tarea 1 de 3",
      nota: "Aún no practicó sin IA. Conviene escribirle.",
      alerta: { tipo: "se-traba", texto: "Se traba en la pista 1" },
    },
  ],
  esEjemplo: true,
};

export const MATERIALES_CLASE_MOCK = [
  "Guía de sensores industriales.pdf",
  "Hoja técnica de sensores inductivos.pdf",
];

export const DETALLES_ALUMNO_MOCK: Record<string, DetalleAlumno> = {
  ana: {
    alumno: CLASE_MOCK.alumnos[0]!,
    clase: "Sensores industriales",
    ultimoAcceso: "hoy a las 10:42",
    usoEscalera: [
      { texto: "Pista 1: la usó y siguió.", usado: true },
      { texto: "Pista 2: la usó para elegir entre dos sensores.", usado: true },
      { texto: "Paso a paso: no lo necesitó.", usado: false },
      { texto: "Respuesta final: se desbloqueó tras su intento.", usado: true },
    ],
    resueltosSinIa: { hechos: 2, total: 5 },
    competencias: [
      { etiqueta: "Formular instrucciones", porcentaje: 70 },
      { etiqueta: "Verificar información", porcentaje: 55 },
      { etiqueta: "Reconocer límites de la IA", porcentaje: 60 },
    ],
    conversacion: [
      { autor: "alumno", etiqueta: "Ana", texto: "No sé qué sensor sirve para botellas de vidrio." },
      {
        autor: "frobi",
        etiqueta: "FROBI · pista 1",
        texto: "¿De qué material es la botella? Revisa en tu guía qué detecta cada sensor.",
      },
      { autor: "alumno", etiqueta: "Ana", texto: "Es vidrio. Creo que el inductivo no." },
    ],
    sugerencia: "Ana ya usa bien las pistas. Propón un ejercicio que resuelva sin IA.",
    esEjemplo: true,
  },
  luis: {
    alumno: CLASE_MOCK.alumnos[1]!,
    clase: "Sensores industriales",
    ultimoAcceso: "ayer a las 18:05",
    usoEscalera: [
      { texto: "Pista 1: la abrió tres veces sin avanzar.", usado: true },
      { texto: "Pista 2: todavía no llega.", usado: false },
      { texto: "Paso a paso: no lo abrió.", usado: false },
      { texto: "Respuesta final: sigue bloqueada, falta su intento.", usado: false },
    ],
    resueltosSinIa: { hechos: 0, total: 5 },
    competencias: [
      { etiqueta: "Formular instrucciones", porcentaje: 35 },
      { etiqueta: "Verificar información", porcentaje: 30 },
      { etiqueta: "Reconocer límites de la IA", porcentaje: 40 },
    ],
    conversacion: [
      { autor: "alumno", etiqueta: "Luis", texto: "¿Cuál es la respuesta?" },
      {
        autor: "frobi",
        etiqueta: "FROBI · pista 1",
        texto: "Primero revisa en tu guía qué material detecta cada sensor.",
      },
    ],
    sugerencia: "Luis se traba en la pista 1. Repasa con él la tabla de materiales de la guía.",
    esEjemplo: true,
  },
};
