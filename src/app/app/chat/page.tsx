"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";

type Message = { role: "user" | "assistant"; content: string };

export default function AIChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "J-ROC AI online. Tell me what you want built, changed, tested, or launched." },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [provider, setProvider] = useState("checking");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!localStorage.getItem("jroc_token")) window.location.href = "/login";
    fetch("/api/intelligence/status", { headers: { Authorization: `Bearer ${localStorage.getItem("jroc_token") || ""}` } })
      .then(r => r.json()).then(d => setProvider(d.openai_configured ? d.model : "fallback routing"))
      .catch(() => setProvider("offline"));
  }, []);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  async function send() {
    const message = input.trim();
    if (!message || busy) return;
    setInput("");
    setMessages(m => [...m, { role: "user", content: message }]);
    setBusy(true);
    try {
      const token = localStorage.getItem("jroc_token") || "";
      const response = await fetch("/api/intelligence/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message, context: { source: "jroc-workspace-chat" } }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "J-ROC intelligence unavailable");
      setMessages(m => [...m, { role: "assistant", content: data.content }]);
    } catch (error) {
      setMessages(m => [...m, { role: "assistant", content: `System error: ${error instanceof Error ? error.message : "request failed"}` }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{minHeight:"100vh",background:"#050810",color:"#eef7ff",padding:"32px",fontFamily:"Inter,system-ui,sans-serif"}}>
      <div style={{maxWidth:1100,margin:"0 auto"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:24}}>
          <div><Link href="/app" style={{color:"#76e7ff",textDecoration:"none"}}>← WORKSPACE</Link><h1 style={{margin:"12px 0 4px",fontSize:36}}>J-ROC AI</h1><p style={{opacity:.65}}>Primary intelligence gateway · {provider}</p></div>
          <span style={{border:"1px solid #214458",borderRadius:999,padding:"8px 14px",fontSize:12}}>SECURE SESSION</span>
        </div>
        <section style={{minHeight:600,border:"1px solid #173040",borderRadius:24,background:"rgba(10,18,30,.82)",boxShadow:"0 20px 80px rgba(0,0,0,.35)",display:"flex",flexDirection:"column"}}>
          <div style={{padding:24,borderBottom:"1px solid #173040"}}><b>COMMAND CONVERSATION</b><span style={{float:"right",opacity:.5,fontSize:12}}>J-ROC builds from your instructions</span></div>
          <div style={{flex:1,padding:24,overflowY:"auto"}}>
            {messages.map((m,i)=><div key={i} style={{display:"flex",justifyContent:m.role==="user"?"flex-end":"flex-start",marginBottom:16}}>
              <div style={{maxWidth:"78%",padding:"14px 16px",borderRadius:16,background:m.role==="user"?"#123447":"#0d1623",border:"1px solid #1b3b4d",whiteSpace:"pre-wrap",lineHeight:1.55}}>{m.content}</div>
            </div>)}
            {busy && <div style={{opacity:.6}}>J-ROC is thinking…</div>}
            <div ref={endRef}/>
          </div>
          <div style={{padding:18,borderTop:"1px solid #173040",display:"flex",gap:12}}>
            <textarea value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send();}}} placeholder="Tell J-ROC what to build…" rows={2} style={{flex:1,resize:"none",borderRadius:14,border:"1px solid #24485b",background:"#07101b",color:"#fff",padding:14,fontSize:15,outline:"none"}} />
            <button onClick={send} disabled={busy||!input.trim()} style={{alignSelf:"stretch",padding:"0 22px",border:0,borderRadius:14,background:"#68e5ff",color:"#031019",fontWeight:800,cursor:busy?"wait":"pointer"}}>{busy?"RUNNING":"SEND"}</button>
          </div>
        </section>
      </div>
    </main>
  );
}
