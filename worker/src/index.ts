import { Container, getContainer } from "@cloudflare/containers";
import { JrocComputeContainer } from "./container";
import { JrocCoordinator } from "./durable";
import { JrocMissionWorkflow } from "./workflows";
import { dispatchWorker, embedAndSearch, embedAndStore, runFreeTierAI } from "./platform";

export interface Env {
  DB: D1Database;
  CACHE: KVNamespace;
  ASSETS_BUCKET: R2Bucket;
  ASSETS: Fetcher;
  AI: Ai;
  MISSION_QUEUE: Queue;
  MEMORY_INDEX: VectorizeIndex;
  JROC_COORDINATOR: DurableObjectNamespace<JrocCoordinator>;
  JROC_COMPUTE_CONTAINER: DurableObjectNamespace<JrocComputeContainer>;
  JROC_MISSION_WORKFLOW: Workflow;
  API_ORIGIN?: string;
  ENVIRONMENT?: string;
  DISPATCHER?: any;
  BROWSER?: any;
}

const json = (data: unknown, init: ResponseInit = {}) => new Response(JSON.stringify(data), {
  ...init,
  headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...(init.headers || {}) },
});

export { JrocComputeContainer, JrocCoordinator, JrocMissionWorkflow };

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/api/health") {
      const db = await env.DB.prepare("SELECT 1 AS ok").first<{ ok: number }>();
      await env.CACHE.put("health:last", new Date().toISOString(), { expirationTtl: 60 });
      return json({ ok: true, service: "jrocai-cloudflare-edge", cloud: "J-ROC Cloud", database: db?.ok === 1, cache: true, objectStorage: Boolean(env.ASSETS_BUCKET), environment: env.ENVIRONMENT || "production" });
    }

    if (url.pathname === "/api/edge/status") {
      return json({ ok: true, service: "jrocai-edge", cloud: "J-ROC Cloud", stage: 35, bindings: { d1: true, kv: true, r2: true, queues: true, workflows: true, durableObjects: true, containers: true, workersAI: true, vectorize: true } });
    }

    if (url.pathname === "/api/cloud/status") {
      const row = await env.DB.prepare("SELECT COUNT(*) AS count FROM cloud_resources").first<{ count: number }>();
      return json({ ok: true, cloud: "J-ROC Cloud", edge: "Cloudflare Workers", stage: 35, resource_count: row?.count ?? 0, services: ["DNS","TLS","Workers","Containers","Durable Objects","D1","KV","R2","Queues","Workflows","Workers AI","AI Gateway","Vectorize"] });
    }

    if (url.pathname === "/api/compute/status") {
      return json({ ok: true, stage: 32, compute: "J-ROC Compute Cloud", provider: "cloudflare", container: "JrocComputeContainer", max_instances: 3, instance_type: "lite", internet_egress: false });
    }

    if (url.pathname.startsWith("/api/compute/container/")) {
      const workerId = url.pathname.split("/").filter(Boolean).pop() || "default";
      const container = getContainer(env.JROC_COMPUTE_CONTAINER, workerId);
      return container.fetch(request);
    }

    if (url.pathname === "/api/queue/mission" && request.method === "POST") {
      const payload = await request.json();
      await env.MISSION_QUEUE.send(payload);
      return json({ ok: true, queued: true, queue: "jrocai-missions" }, { status: 202 });
    }

    if (url.pathname === "/api/platform/status") {
      return json({ ok: true, stage: 35, platform: "J-ROC Cloudflare Evolution Layer", workersForPlatforms: Boolean(env.DISPATCHER), browserRun: Boolean(env.BROWSER), workersAI: true, vectorize: true, observability: true, cron: true, queueConsumer: true });
    }

    if (url.pathname === "/api/platform/dispatch" && request.method === "POST") {
      const body: any = await request.json();
      const workerName = String(body.worker || "").trim();
      if (!workerName) return json({ ok: false, error: "worker is required" }, { status: 400 });
      return dispatchWorker(env, workerName, request);
    }

    if (url.pathname === "/api/ai/infer" && request.method === "POST") {
      const body: any = await request.json();
      const prompt = String(body.prompt || "").trim();
      if (!prompt) return json({ ok: false, error: "prompt is required" }, { status: 400 });
      return json({ ok: true, ...(await runFreeTierAI(env, prompt, body.model || "@cf/meta/llama-3.1-8b-instruct")) });
    }

    if (url.pathname === "/api/memory/search" && request.method === "POST") {
      const body: any = await request.json();
      const query = String(body.query || "").trim();
      if (!query) return json({ ok: false, error: "query is required" }, { status: 400 });
      return json({ ok: true, query, results: await embedAndSearch(env, query, Number(body.topK || 5)) });
    }

    if (url.pathname === "/api/memory/upsert" && request.method === "POST") {
      const body: any = await request.json();
      const id = String(body.id || crypto.randomUUID());
      const text = String(body.text || "").trim();
      if (!text) return json({ ok: false, error: "text is required" }, { status: 400 });
      return json({ ok: true, ...(await embedAndStore(env, id, text, body.metadata || {})) });
    }

    if (url.pathname === "/api/browser/status") {
      return json({ ok: true, browserRun: Boolean(env.BROWSER), note: "Browser Run requires the Browser binding and applicable Cloudflare account access." });
    }

    if (url.pathname === "/api/ai/status") {
      return json({ ok: true, workersAI: true, gateway: "AI Gateway-compatible binding", note: "Model usage follows Cloudflare account plan and configured AI routing." });
    }

    if (url.pathname === "/api/memory/status") {
      return json({ ok: true, vectorize: true, index: "jrocai-memory", purpose: "J-ROC semantic memory" });
    }

    if (url.pathname.startsWith("/api/edge/")) return json({ ok: true, service: "jrocai-edge", path: url.pathname });

    if (env.API_ORIGIN && url.pathname.startsWith("/api/")) {
      const origin = env.API_ORIGIN.replace(/\/$/, "");
      const target = new URL(origin + url.pathname + url.search);
      return fetch(new Request(target, request));
    }

    return env.ASSETS.fetch(request);
  },

  async scheduled(_controller: ScheduledController, env: Env): Promise<void> {
    const timestamp = new Date().toISOString();
    await env.CACHE.put("jroc:edge:heartbeat", timestamp, { expirationTtl: 300 });
    console.log(JSON.stringify({ event: "JROC_EDGE_HEARTBEAT", stage: 35, timestamp }));
  },

  async queue(batch: MessageBatch<any>, _env: Env): Promise<void> {
    for (const message of batch.messages) {
      console.log(JSON.stringify({ event: "JROC_MISSION_QUEUE_RECEIVED", payload: message.body }));
      message.ack();
    }
  },
};
