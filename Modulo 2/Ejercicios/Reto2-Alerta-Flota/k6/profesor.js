// k6 OFICIAL del profesor, adaptado para correr contra este sistema.
// Original sin tocar: Modulo 2/Material-Clase/k6-script-profesor.js (recibido el 06/10/2026).
//
// Diferencias con el original (las únicas):
//   1. La URL: el original apunta a la API Gateway del profesor en AWS; aquí va a nuestro gateway.
//   2. handleSummary: escribe logs/k6-summary.json, que leen scripts/medir.py y el panel.
// Todo lo demás (VUs, iteraciones, sleep, payload, cálculo del Emergency) es idéntico a propósito:
// la prueba vale porque es el script del profesor, con sus defectos incluidos (ver README).
//
//   k6 run k6/profesor.js
import http from 'k6/http';
import { check, sleep } from 'k6' ;
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';

// [CAMBIO 1] El original usa 'https://xstkjuct1f.execute-api.us-east-2.amazonaws.com/prod/event-notification'.
const TARGET_URL = __ENV.TARGET_URL || 'http://localhost:8080/events';

export const options = {
  vus: 10,           // 10 usuarios virtuales
  iterations: 1000,  // Total de peticiones
  duration: '30s',   // Tiempo total
};

// Índice global para iteraciones (variable compartida entre VUs)
let globalIndex = 0;

// Bloque para incrementar el índice global de forma segura
function getGlobalIndex() {
  return globalIndex++;
}

// Generar placa de vehículo
function generateVehiclePlate() {
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const numbers = '0123456789';
  return `${letters.charAt(Math.floor(Math.random() * letters.length))}${letters.charAt(Math.floor(Math.random() * letters.length))}${letters.charAt(Math.floor(Math.random() * letters.length))}-${numbers.charAt(Math.floor(Math.random() * numbers.length))}${numbers.charAt(Math.floor(Math.random() * numbers.length))}${numbers.charAt(Math.floor(Math.random() * numbers.length))}`;
}

// Generar coordenadas
function generateCoordinates() {
  return {
    latitude: (Math.random() * 180 - 90).toFixed(6),
    longitude: (Math.random() * 360 - 180).toFixed(6),
  };
}

// Generar tipo de mensaje usando índice global calculado
function generateType(globalIndex) {
  return globalIndex < 999 ? 'Position' : 'Emergency';
}

// Función principal
export default function () {
  // Cálculo del índice global
  const globalIndex = (__VU - 1) * (options.iterations / options.vus) + __ITER;

  const payload = JSON.stringify({
    type: generateType(globalIndex),
    vehicle_plate: generateVehiclePlate(),
    coordinates: generateCoordinates(),
    status: 'OK',
  });

  const headers = { 'Content-Type': 'application/json' };

  const res = http.post(TARGET_URL, payload, { headers });

  console.log(JSON.stringify({
    globalIndex,
    type: payload.type,
    timestamp: new Date().toISOString(),
    status: res.status,
    duration: res.timings.duration
  }));

  check(res, {
    'is status 200': (r) => r.status === 200,
  });

  sleep(0.1);
}

// [CAMBIO 2] Mismo formato que k6/carga.js para que medir.py y el panel lean la corrida.
export function handleSummary(data) {
  const endedAt = new Date(); // ≈ fin del último envío (cota superior, del orden de ms)
  const startedAt = new Date(endedAt.getTime() - data.state.testRunDurationMs);
  const resumen = {
    script: 'profesor',
    started_at: startedAt.toISOString(),
    ended_at: endedAt.toISOString(),
    emergencies: null, // lo decide el script del profesor, no un parámetro
    sleep_s: 0.1,
    metrics: {
      http_reqs: data.metrics.http_reqs.values.count,
      http_req_failed_rate: data.metrics.http_req_failed.values.rate,
      http_req_duration_p95_ms: data.metrics.http_req_duration.values['p(95)'],
      checks_rate: data.metrics.checks.values.rate,
    },
  };
  return {
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
    [__ENV.SUMMARY_PATH || 'logs/k6-summary.json']: JSON.stringify(resumen, null, 2),
  };
}
