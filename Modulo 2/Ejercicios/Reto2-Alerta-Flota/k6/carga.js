// k6 PROVISIONAL del Reto 2: imita la salida de referencia del enunciado
// (1 escenario, 10 VUs, 1000 iteraciones compartidas, maxDuration 30s).
// Se reemplaza por el k6 oficial cuando el profesor lo entregue.
//
//   k6 run k6/carga.js                    ráfaga: en local termina en < 1 s
//   k6 run -e SLEEP_S=0.28 k6/carga.js    ritmo de referencia: ~35 req/s durante ~28 s
//   k6 run -e EMERGENCIES=20 k6/carga.js
import http from 'k6/http';
import exec from 'k6/execution';
import { check, sleep } from 'k6';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';

const TARGET_URL = __ENV.TARGET_URL || 'http://localhost:8080/events';
const TOTAL = 1000;
// Pausa por iteración. La salida de referencia (35.69 req/s, ~28 s) refleja la latencia de AWS
// (~176 ms); en local cada petición tarda ~2 ms, así que sin pausa todo llega como ráfaga.
const SLEEP_S = Number(__ENV.SLEEP_S || 0);
const EMERGENCIES = __ENV.EMERGENCIES !== undefined ? Number(__ENV.EMERGENCIES) : 5;
// La última iteración siempre es Emergency: es el peor caso para la medida de la rúbrica.
const EVERY = EMERGENCIES > 0 ? Math.floor(TOTAL / EMERGENCIES) : 0;

export const options = {
  scenarios: {
    flota: { executor: 'shared-iterations', vus: 10, iterations: TOTAL, maxDuration: '30s' },
  },
};

export default function () {
  const i = exec.scenario.iterationInTest;
  const emergency = EVERY > 0 && i % EVERY === EVERY - 1;
  const payload = {
    type: emergency ? 'Emergency' : 'Position',
    vehicle_plate: `VFH-${String(i % 1000).padStart(3, '0')}`,
    coordinates: { latitude: 3.4516 + i / 10000, longitude: -76.532 },
    status: 'OK',
  };
  const res = http.post(TARGET_URL, JSON.stringify(payload), {
    headers: { 'Content-Type': 'application/json' },
    tags: { type: payload.type },
  });
  check(res, { 'is status 200': (r) => r.status === 200 });
  if (SLEEP_S > 0) sleep(SLEEP_S);
}

export function handleSummary(data) {
  const endedAt = new Date(); // ≈ fin del último envío (cota superior, del orden de ms)
  const startedAt = new Date(endedAt.getTime() - data.state.testRunDurationMs);
  const resumen = {
    started_at: startedAt.toISOString(),
    ended_at: endedAt.toISOString(),
    emergencies: EMERGENCIES,
    sleep_s: SLEEP_S,
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
