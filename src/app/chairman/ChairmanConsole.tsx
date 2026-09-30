"use client";
import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

type Panel = "overview" | "command" | "executives" | "workforce" | "missions" | "apps" | "security" | "infrastructure";
type ApiState = { dashboard?: any; executives?: any; workforce?: any; missions?: any; apps?: any; security?: any; infrastructure?: any; metrics?: any };
const panels: { id: Panel; label: string; icon: string }[] = [
  { id: "overview", label: "Chairman Overview", icon: "01" }, { id: "command", label: "Command Center", icon: "02" },
  { id: "executives", label: "Executive Council", icon: "03" }, { id: "workforce", label: "AI Workforce", icon: "04" },
  { id: "missions", label: "Mission Control", icon: "05" }, { id: "apps", label: "Platform & Apps", icon: "06" },
  { id: "security", label: "Security & Audit", icon: "07" }, { id: "infrastructure", label: "Infrastructure", icon: "08" },
];
function tokenHeaders(): HeadersInit { if (typeof window === "undefined") return {}; const token = window.localStorage.getItem("jroc_token") || window.localStorage.getItem("access_token"); return token ? { Authorization: "Bearer " + token } : {}; }
async function api(path: string, init?: RequestInit) {
  const response = await fetch(path, { ...init, headers: { ...tokenHeaders(), ...(init?.headers || {}) }, cache: "no-store" });
  if (!response.ok) throw new Error(String(response.status) + " " + response.statusText);
  return response.json();
}
function Stat({ label, value, detail }: { label: string; value: string | number; detail?: string }) {
  return <div className="card chairman-stat"><div className="label">{label}</div><div className="kpi">{value}</div>{detail && <div className="small">{detail}</div>}</div>;
}
export default function ChairmanConsole() {
  const [panel, setPanel] = useState<Panel>("overview");
  const [input, setInput] = useState("");
  const [logs, setLogs] = useState<string[]>(["CHAIRMAN SUITE: initialized.","GOVERNANCE: Chairman authority boundary active.","COMMAND ENGINES: Primary / Validator / Healer / Consensus.","AUTO-REPAIR: Coder + Healer workforce registered."]);
  const [data, setData] = useState<ApiState>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [briefing, setBriefing] = useState("No briefing requested.");
  const load = async () => {
    setLoading(true); setError("");
    try {
      const result = await Promise.all([api("/api/chairman/dashboard"),api("/api/chairman/executives"),api("/api/chairman/workforce"),api("/api/chairman/missions"),api("/api/chairman/apps"),api("/api/chairman/security"),api("/api/chairman/infrastructure"),api("/api/chairman/metrics")]);
      setData({dashboard:result[0],executives:result[1],workforce:result[2],missions:result[3],apps:result[4],security:result[5],infrastructure:result[6],metrics:result[7]});
      setLogs(x => x.concat("SYSTEM: Chairman telemetry synchronized."));
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to reach Chairman API"); setLogs(x => x.concat("SYSTEM: API telemetry unavailable; showing local command shell.")); }
    finally { setLoading(false); }
  };
  useEffect(() => {
    (async () => {
      try {
        const response = await fetch("/api/auth/me", { credentials: "include", cache: "no-store" });
        if (!response.ok) throw new Error("unauthorized");
        const identity = await response.json();
        if (identity.role !== "CHAIRMAN") throw new Error("chairman");
        window.localStorage.setItem("jroc_role", identity.role);
        void load();
      } catch {
        window.localStorage.removeItem("jroc_token");
        window.localStorage.removeItem("jroc_role");
        window.location.replace("/chairman/login");
      }
    })();
  }, []);
  const counts = data.dashboard?.counts || {}; const operations = data.dashboard?.operations || {};
  const workers = data.workforce?.workers || []; const executives = data.executives?.executives || [];
  const missions = data.missions?.missions || []; const apps = data.apps?.apps || []; const events = data.security?.recent_events || [];
  const available = data.workforce?.capacity ?? 0; const telemetry = data.metrics?.telemetry || {};
  async function dispatch(e: FormEvent) {
    e.preventDefault(); const value = input.trim(); if (!value) return;
    setLogs(x => x.concat("CHAIRMAN DIRECTIVE: " + value, "COMMAND BRAIN: dispatching authorized directive...")); setInput("");
    try {
      const result = await api("/api/chairman/command", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ objective: value, context: { source: "chairman-suite" } }) });
      setLogs(x => x.concat("COMMAND RESULT: accepted.", JSON.stringify(result.result ?? result)));
      void load();
    } catch (e) { setLogs(x => x.concat("COMMAND RESULT: " + (e instanceof Error ? e.message : "request failed"))); }
  }
  async function requestBriefing() {
    setBriefing("Generating Chairman executive briefing...");
    try { const result = await api("/api/chairman/briefing"); setBriefing(typeof result.briefing === "string" ? result.briefing : JSON.stringify(result.briefing)); }
    catch (e) { setBriefing("Briefing unavailable: " + (e instanceof Error ? e.message : "request failed")); }
  }
  return <div className="chairman-suite">
    <aside className="chairman-rail"><div className="chairman-seal"><span>J</span></div><div className="rail-title">CHAIRMAN<br/><strong>SUITE</strong></div><div className="rail-status"><i/> AUTHORITY ACTIVE</div>
      <nav>{panels.map(item => <button key={item.id} className={panel === item.id ? "rail-link active" : "rail-link"} onClick={() => setPanel(item.id)}><span>{item.icon}</span>{item.label}</button>)}</nav>
      <div className="rail-bottom"><Link href="/" className="rail-link"><span>⌂</span>Home Base</Link><Link href="/network" className="rail-link"><span>∞</span>Network & Cloud</Link></div>
    </aside>
    <main className="chairman-main"><header className="chairman-top"><div><div className="eyebrow">J-ROC AI PLATFORM // LEVEL 0 GOVERNANCE</div><h1>CHAIRMAN <span>OFFICE</span></h1></div><div className="top-actions"><div className="live-pill"><i/> {loading ? "SYNCING" : "LIVE CONTROL PLANE"}</div><button className="refresh" onClick={() => void load()}>SYNC</button><button className="refresh" onClick={() => void requestBriefing()}>BRIEFING</button></div></header>
      {error && <div className="chairman-alert">API STATUS: {error}. The suite remains available in command-shell mode.</div>}
      {panel === "overview" && <section className="panel-stack"><div className="office-banner"><div><div className="eyebrow">PRIVATE EXECUTIVE OFFICE</div><h2>Chairman Command Center</h2><p>One control surface for governance, missions, executives, workforce, intelligence, infrastructure, security, finance and autonomous recovery.</p></div><div className="authority-card"><div className="label">AUTHORITY</div><strong>CHAIRMAN</strong><small>Supreme governance layer</small></div></div>
        <div className="grid grid4 chairman-grid"><Stat label="Organizations" value={counts.organizations ?? "—"}/><Stat label="Active Agents" value={counts.agents ?? "—"}/><Stat label="Active Missions" value={operations.active_missions ?? "—"}/><Stat label="AI Workforce" value={workers.length || "—"} detail={String(available) + " available"}/></div>
        <div className="grid grid3"><div className="card"><div className="eyebrow">OPERATIONS</div><h2>Mission Health</h2><div className="metric-line"><span>Completed</span><b>{operations.completed_missions ?? 0}</b></div><div className="metric-line"><span>Failed / Rejected</span><b>{operations.failed_missions ?? 0}</b></div><div className="metric-line"><span>Telemetry Success</span><b>{telemetry.success_rate != null ? Math.round(telemetry.success_rate * 100) + "%" : "—"}</b></div></div>
          <div className="card"><div className="eyebrow">COMMAND ENGINES</div><h2>Four-Brain Governance</h2><div className="engine-list"><span>PRIMARY <b>READY</b></span><span>VALIDATOR <b>READY</b></span><span>HEALER <b>READY</b></span><span>CONSENSUS <b>READY</b></span></div></div>
          <div className="card"><div className="eyebrow">EXECUTIVE INTELLIGENCE</div><h2>Chairman Briefing</h2><div className="briefing-box">{briefing}</div><button className="suite-button" onClick={() => void requestBriefing()}>GENERATE BRIEFING</button></div></div>
      </section>}
      {panel === "command" && <section className="grid grid2"><div className="card command-card"><div className="eyebrow">COMMAND CONSOLE</div><h2>Chairman Directive Console</h2><p className="small">Issue a directive to the command layer. Execution remains subject to authorization and validation.</p><div className="console">{logs.map((x,i)=><div className="log" key={i}>&gt; {x}</div>)}</div><form className="prompt" onSubmit={dispatch}><input value={input} onChange={e=>setInput(e.target.value)} placeholder="Enter a Chairman directive..."/><button>DISPATCH</button></form></div><div className="card"><div className="eyebrow">AUTHORITY STACK</div><h2>Governance Chain</h2><div className="governance-stack">{["CHAIRMAN","COMMAND BRAIN","PRIMARY BRAIN","VALIDATOR BRAIN","CONSENSUS","EXECUTIVE COUNCIL","DEPARTMENTS","WORKFORCE","AUDIT + MEMORY"].map((x,i)=><div key={x}><span>{String(i+1).padStart(2,"0")}</span><b>{x}</b></div>)}</div></div></section>}
      {panel === "executives" && <section className="card"><div className="eyebrow">EXECUTIVE OFFICE</div><h2>AI Executive Council</h2><div className="suite-table">{executives.map((x:any)=><div className="suite-row" key={x.key}><b>{x.key}</b><span>{x.role}</span><em>{x.status}</em></div>)}</div></section>}
      {panel === "workforce" && <section className="card"><div className="eyebrow">OPERATIONS OFFICE</div><h2>AI Workforce Command</h2><div className="grid grid3 chairman-grid"><Stat label="Workers" value={workers.length}/><Stat label="Available" value={available}/><Stat label="Assigned / Busy" value={Math.max(0,workers.length-available)}/></div><div className="suite-table">{workers.map((x:any)=><div className="suite-row" key={x.id}><b>{x.name}</b><span>{x.department} / {x.role}</span><em>{x.status}</em></div>)}</div></section>}
      {panel === "missions" && <section className="card"><div className="eyebrow">MISSION CONTROL</div><h2>Chairman Missions</h2><div className="suite-table">{missions.length ? missions.map((x:any)=><div className="suite-row" key={x.id}><b>#{x.id} {x.objective}</b><span>{x.decision || "Awaiting decision"}</span><em>{x.status}</em></div>) : <div className="empty-state">No Chairman missions recorded yet.</div>}</div></section>}
      {panel === "apps" && <section className="card"><div className="eyebrow">PLATFORM OFFICE</div><h2>Organizations & Applications</h2><div className="grid grid3 chairman-grid"><Stat label="Organizations" value={counts.organizations ?? 0}/><Stat label="Applications" value={apps.length || counts.apps || 0}/><Stat label="Marketplace Items" value={counts.marketplace_items ?? 0}/></div><div className="suite-table">{apps.map((x:any)=><div className="suite-row" key={x.id}><b>{x.name}</b><span>{x.slug}</span><em>{x.status}</em></div>)}</div></section>}
      {panel === "security" && <section className="card"><div className="eyebrow">SECURITY OFFICE</div><h2>Security & Audit</h2><div className="grid grid3 chairman-grid"><Stat label="Risk Level" value={data.security?.risk_level ?? "UNKNOWN"}/><Stat label="Failed Events" value={data.security?.failed_events ?? 0}/><Stat label="Audit Events" value={data.metrics?.audit?.events ?? 0}/></div><div className="suite-table">{events.map((x:any,i:number)=><div className="suite-row" key={i}><b>{x.event}</b><span>{x.resource}</span><em>{x.success ? "SUCCESS" : "FAILED"}</em></div>)}</div></section>}
      {panel === "infrastructure" && <section className="card"><div className="eyebrow">INFRASTRUCTURE OFFICE</div><h2>J-ROC Runtime</h2><div className="grid grid3 chairman-grid"><Stat label="API" value={data.infrastructure?.api?.status ?? "—"}/><Stat label="Database" value={data.infrastructure?.database?.status ?? "—"}/><Stat label="Telemetry" value={data.infrastructure?.telemetry?.events ?? 0}/></div><div className="infra-grid">{Object.entries(data.infrastructure || {}).map(([key,value]:any)=><div className="infra-cell" key={key}><span>{key}</span><b>{typeof value === "object" ? value.status ?? "configured" : value}</b></div>)}</div></section>}
    </main></div>;
}