"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";

export default function LoginPage(){
 const [username,setUsername]=useState(""); const [password,setPassword]=useState(""); const [error,setError]=useState(""); const [busy,setBusy]=useState(false);
 async function submit(e:FormEvent){e.preventDefault();setBusy(true);setError("");
  try{
   const body=new URLSearchParams({username,password});
   const res=await fetch("/api/auth/login",{method:"POST",credentials:"include",headers:{"Content-Type":"application/x-www-form-urlencoded"},body});
   const data=await res.json().catch(()=>({}));
   if(!res.ok)throw new Error(data.detail||"Unable to sign in");
   localStorage.setItem("jroc_token",data.access_token);
   localStorage.setItem("jroc_role",data.role||"USER");
   window.location.href="/app";
  }catch(err){setError(err instanceof Error?err.message:"Unable to sign in");}finally{setBusy(false);}
 }
 return <div className="chairman-login-page"><div className="login-grid"/><div className="login-card">
  <div className="login-orb"><div><strong>J</strong><small>J-ROC AI</small></div></div><div className="eyebrow">J-ROC AI // WORKSPACE ACCESS</div><h1>Enter your <span>workspace.</span></h1>
  <p>Your customer workspace is the product layer. Chairman access remains a separate private command environment.</p>
  <form onSubmit={submit}><label>IDENTITY ID<input value={username} onChange={e=>setUsername(e.target.value)} autoComplete="username" required/></label><label>PRIVATE KEY<input type="password" value={password} onChange={e=>setPassword(e.target.value)} autoComplete="current-password" required/></label>{error&&<div className="login-error">{error}</div>}<button disabled={busy}>{busy?"VERIFYING...":"VERIFY & ENTER WORKSPACE"}</button></form>
  <div className="login-footer"><Link href="/get-started">Create / request access</Link><Link href="/chairman/login">Chairman Login →</Link></div>
 </div></div>;
}