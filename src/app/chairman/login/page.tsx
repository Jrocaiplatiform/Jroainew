"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";

export default function ChairmanLoginPage() {
  const [username,setUsername]=useState(""); const [password,setPassword]=useState("");
  const [error,setError]=useState(""); const [busy,setBusy]=useState(false);

  async function login(e:FormEvent){
    e.preventDefault(); setBusy(true); setError("");
    try{
      const body=new URLSearchParams({username,password});
      const response=await fetch("/api/auth/login",{method:"POST",credentials:"include",headers:{"Content-Type":"application/x-www-form-urlencoded"},body});
      const data=await response.json();
      if(!response.ok) throw new Error(data.detail || "Access denied");
      if(data.role !== "CHAIRMAN") throw new Error("Chairman authority required.");
      localStorage.setItem("jroc_token",data.access_token);
      localStorage.setItem("jroc_role",data.role || "");
      window.location.href="/chairman";
    }catch(err){setError(err instanceof Error ? err.message : "Unable to authenticate");}
    finally{setBusy(false);}
  }

  return <main className="chairman-login-page">
    <div className="login-grid"/>
    <section className="login-card">
      <div className="login-orb"><strong>J</strong><small>J-ROC AI</small></div>
      <div className="eyebrow">SECURE EXECUTIVE ACCESS // LEVEL 0</div>
      <h1>Enter the <span>Command Layer.</span></h1>
      <p>Identity verification is required before the Chairman Office and private operating systems become visible.</p>
      <div className="access-mode"><span className="active">CHAIRMAN</span><span>EXECUTIVE</span><span>OPERATOR</span></div>
      <form onSubmit={login}>
        <label>IDENTITY ID<input value={username} onChange={e=>setUsername(e.target.value)} autoComplete="username" placeholder="Chairman username" required/></label>
        <label>PRIVATE KEY<input type="password" value={password} onChange={e=>setPassword(e.target.value)} autoComplete="current-password" placeholder="Password" required/></label>
        {error && <div className="login-error">{error}</div>}
        <button disabled={busy}>{busy ? "VERIFYING IDENTITY..." : "VERIFY & ENTER"}</button>
      </form>
      <div className="identity-row"><span>ACCESS STATUS</span><b>AUTHENTICATION REQUIRED</b></div>
      <div className="security-note">The public website remains separate from the private command plane. Do not share credentials or place secrets in browser-visible code.</div>
      <div className="login-footer"><Link href="/">← J-ROC AI</Link><span>PRIVATE // AUTHORIZED ONLY</span></div>
    </section>
  </main>;
}