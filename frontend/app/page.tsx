"use client";
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useDropzone } from "react-dropzone";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

type FolderNode = { path: string; dirs: string[]; files: string[]; };

export default function Home() {
  const [folders, setFolders] = useState<FolderNode[]>([]);
  const [selectedScopes, setSelectedScopes] = useState<string[]>([]);
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState<{role:"user"|"assistant",content:string,citations?:any[]}[]>([]);
  const [folderPath, setFolderPath] = useState("");

  useEffect(()=>{ fetchFolders(); },[]);

  async function fetchFolders(){
    const {data} = await axios.get(`${API_BASE}/folders`);
    setFolders(data.folders);
  }

  function toggleScope(path:string){
    setSelectedScopes(prev => prev.includes(path) ? prev.filter(p=>p!==path) : [...prev, path]);
  }

  const {getRootProps, getInputProps, isDragActive} = useDropzone({
    onDrop: async (acceptedFiles:File[]) => {
      if(!folderPath){ alert("׳‘׳—׳¨/׳™ ׳×׳™׳§׳™׳™׳” ׳׳”׳¢׳׳׳”"); return; }
      for(const file of acceptedFiles){
        const form = new FormData();
        form.append("folder_path", folderPath);
        form.append("file", file);
        await axios.post(`${API_BASE}/upload`, form, { headers: {"Content-Type":"multipart/form-data"} });
      }
      await fetchFolders();
      alert("׳”׳¢׳׳׳” ׳”׳•׳©׳׳׳”");
    }
  });

  async function send(){
    if(!message.trim()) return;
    const userMsg = {role:"user" as const, content: message};
    setChat(c => [...c, userMsg]);
    setMessage("");
    const {data} = await axios.post(`${API_BASE}/chat`, {
      message: userMsg.content,
      folder_paths: selectedScopes,
      top_k: 6,
      answer_mode: "concise"
    });
    setChat(c => [...c, {role:"assistant", content: data.answer, citations: data.citations}]);
  }

  function renderTree(){
    return (
      <div>
        <div style={{marginBottom:8, fontWeight:600}}>׳×׳™׳§׳™׳•׳×</div>
        {folders.map((f, idx)=>{
          const label = f.path || "[׳©׳•׳¨׳©]";
          return (
            <div key={idx} className="fileRow">
              <span>{label}</span>
              <button className="button" onClick={()=>toggleScope(label)}>
                {selectedScopes.includes(label) ? "׳”׳¡׳¨ ׳¡׳§׳•׳₪" : "׳‘׳—׳¨ ׳¡׳§׳•׳₪"}
              </button>
            </div>
          );
        })}
        <div style={{marginTop:12, fontWeight:600}}>׳‘׳—׳¨ ׳™׳¢׳“ ׳׳”׳¢׳׳׳”</div>
        <input value={folderPath} onChange={e=>setFolderPath(e.target.value)} placeholder="׳׳“׳•׳’׳׳”: ׳—׳•׳–׳™׳/2025" />
        <div className="dropzone" {...getRootProps()} style={{marginTop:8}}>
          <input {...getInputProps()} />
          {isDragActive ? <p>׳©׳—׳¨׳¨/׳™ ׳›׳׳ג€¦</p> : <p>׳’׳¨׳•׳¨/׳™ ׳§׳‘׳¦׳™׳ ׳׳›׳׳</p>}
        </div>
        <button className="button" style={{marginTop:8}} onClick={async ()=>{
          if(!folderPath) return;
          await axios.post(`${API_BASE}/folders`, {path: folderPath});
          await fetchFolders();
        }}>׳¦׳•׳¨ ׳×׳™׳§׳™׳™׳”</button>
      </div>
    );
  }

  function renderChips(){
    return <div className="chips">{selectedScopes.map((s,i)=>(<span key={i} className="chip">@{s}</span>))}</div>;
  }

  return (
    <div className="container">
      <div className="sidebar">{renderTree()}</div>
      <div className="main">
        <div className="toolbar">
          <div style={{fontWeight:700}}>Hebrew RAG Chat ֲ· Dark</div>
          <div style={{marginLeft:8}}>{renderChips()}</div>
        </div>
        <div className="chat">
          {chat.map((m,i)=> (
            <div key={i} className="message">
              <div style={{opacity:.7, fontSize:12}}>{m.role==="user" ? "׳׳×/׳”" : "׳”׳‘׳•׳˜"}</div>
              <div dangerouslySetInnerHTML={{__html: m.content.replace(/\n/g,"<br/>")}} />
              {m.citations && m.citations.length>0 && (
                <div className="citation" style={{marginTop:6}}>
                  ׳¦׳™׳˜׳•׳˜׳™׳: {m.citations.map((c:any)=>`[${c.index}]`).join(" ")}
                </div>
              )}
            </div>
          ))}
        </div>
        <div className="composer">
          <div className="inputRow">
            <input placeholder="׳›׳×׳•׳‘/׳›׳×׳‘׳™ ׳©׳׳׳” ׳‘׳¢׳‘׳¨׳™׳×ג€¦" value={message} onChange={e=>setMessage(e.target.value)}
                   onKeyDown={e=>{ if(e.key==="Enter" && !e.shiftKey) send(); }} />
            <button className="button" onClick={send}>׳©׳׳—</button>
          </div>
        </div>
      </div>
    </div>
  );
}
