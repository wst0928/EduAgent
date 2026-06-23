import React, { useState, useEffect } from "react";
import { ArrowLeft, BookOpen, FileText, Code, ClipboardList, RefreshCw, Loader2, Star } from "lucide-react";

interface ResourceViewerProps {
  topic: string;
  onBack: () => void;
}

interface Resource {
  id?: string;
  title?: string;
  resource_type?: string;
  type?: string;
  content?: string;
  difficulty?: number;
}

const typeMeta: Record<string, { icon: any; label: string; color: string }> = {
  article: { icon: BookOpen, label: "教学文章", color: "#4f46e5" },
  summary: { icon: FileText, label: "知识总结", color: "#0891b2" },
  quiz: { icon: ClipboardList, label: "测验", color: "#d97706" },
  exercise: { icon: Code, label: "练习题", color: "#059669" },
  study_guide: { icon: BookOpen, label: "学习指南", color: "#db2777" },
  code_example: { icon: Code, label: "代码示例", color: "#7c3aed" },
};
const defMeta = { icon: FileText, label: "资源", color: "var(--text-secondary)" };

const renderContent = (content: string) => {
  if (!content) return null;
  const lines = content.split("\n");
  const els: JSX.Element[] = [];
  let inCode = false, codeBuf: string[] = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith("```")) {
      if (inCode) { els.push(<pre key={"c"+i} style={{background:"#1e1e2e",color:"#cdd6f4",borderRadius:8,padding:"12px 16px",overflow:"auto",fontSize:13,lineHeight:1.5,fontFamily:"monospace"}}><code>{codeBuf.join("\n")}</code></pre>); codeBuf = []; inCode = false; }
      else { inCode = true; }
      continue;
    }
    if (inCode) { codeBuf.push(line); continue; }
    if (line.startsWith("### ")) { els.push(<h3 key={i} style={{fontSize:16,fontWeight:600,marginTop:16,marginBottom:8}}>{line.slice(4)}</h3>); continue; }
    if (line.startsWith("## ")) { els.push(<h2 key={i} style={{fontSize:18,fontWeight:600,marginTop:20,marginBottom:8}}>{line.slice(3)}</h2>); continue; }
    if (line.startsWith("# ")) { els.push(<h1 key={i} style={{fontSize:20,fontWeight:700,marginTop:20,marginBottom:10}}>{line.slice(2)}</h1>); continue; }
    if (line.trim() === "") { els.push(<div key={"e"+i} style={{height:6}} />); continue; }
    els.push(<p key={"p"+i} style={{marginBottom:4,fontSize:14,lineHeight:1.6}}>{line}</p>);
  }
  if (inCode && codeBuf.length) els.push(<pre key={"ce"} style={{background:"#1e1e2e",color:"#cdd6f4",borderRadius:8,padding:"12px 16px",overflow:"auto",fontSize:13,lineHeight:1.5,fontFamily:"monospace"}}><code>{codeBuf.join("\n")}</code></pre>);
  return els;
};

export default function ResourceViewer({ topic, onBack }: ResourceViewerProps) {
  const [resources, setResources] = useState<any[]>([]);
  const [selected, setSelected] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  // Load existing resources on mount
  useEffect(() => {
    fetch("/api/v1/resources").then(r=>r.json()).then(d => {
      const list = d.resources || [];
      setResources(list);
      if (list.length > 0) setSelected(list[0]);
    }).catch(() => {});
  }, []);

  const generateResource = async (type: string) => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/resources/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "default", topic, resource_types: [type], difficulty: 1 }),
      });
      const data = await res.json();
      const items = data.resources || [];
      if (items.length > 0) {
        setResources((prev) => [...items, ...prev]);
        setSelected(items[0]);
      } else {
        // Fallback: generate via chat
        const chatRes = await fetch("/api/v1/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: "default", message: "生成关于" + topic + "的" + type + "类型学习资源", workflow: "generate_resources" }),
        });
        const chatData = await chatRes.json();
        if (chatData.reply) {
          const fakeRes = { id: "gen_" + Date.now(), title: topic + " - " + type, resource_type: type, content: chatData.reply, difficulty: 1 };
          setResources((prev) => [fakeRes, ...prev]);
          setSelected(fakeRes);
        }
      }
    } catch { /* ignore */ }
    finally { setLoading(false); }
  };

  const getMeta = (t: string) => typeMeta[t] || defMeta;

  return (
    <div style={{ display: "flex", height: "100%" }}>
      {/* Sidebar */}
      <div style={{ width: 260, background: "var(--bg-card)", borderRight: "1px solid var(--border)", display: "flex", flexDirection: "column", flexShrink: 0 }}>
        <div style={{ padding: "16px 16px 12px", borderBottom: "1px solid var(--border)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <button onClick={onBack} style={{ background:"none", color:"var(--text-secondary)", padding:4, display:"flex" }}><ArrowLeft size={18} /></button>
            <span style={{ fontSize: 14, fontWeight: 600 }}>学习资源</span>
          </div>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 8 }}>主题: {topic}</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
            {["article","summary","exercise","study_guide","code_example"].map((t) => {
              const meta = getMeta(t);
              return (
                <button key={t} onClick={() => generateResource(t)} disabled={loading}
                  style={{ padding: "4px 8px", borderRadius: 6, background: meta.color + "15", color: meta.color, fontSize: 11, fontWeight: 500, border: "none", display: "flex", alignItems: "center", gap: 4 }}>
                  <meta.icon size={12} />
                  {meta.label}
                </button>
              );
            })}
          </div>
          {loading && <p style={{fontSize:11,color:"var(--text-secondary)",marginTop:6}}>生成中...</p>}
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: 8 }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: "var(--text-secondary)", padding: "4px 8px", marginBottom: 4 }}>
            已有资源 ({resources.length})
          </p>
          {resources.length === 0 && (
            <p style={{ fontSize: 13, color: "var(--text-light)", textAlign: "center", padding: 20 }}>点击上方按钮生成学习资源</p>
          )}
          {resources.map((r, i) => {
            const type = r.resource_type || r.type || "article";
            const meta = getMeta(type);
            return (
              <button key={r.id || i} onClick={() => setSelected(r)}
                style={{ width:"100%", padding:"8px 10px", borderRadius:"var(--radius)", background: selected?.id===r.id?"var(--bg)":"transparent", border:"none", textAlign:"left", display:"flex", gap:8, alignItems:"center", marginBottom:2 }}>
                <div style={{ width:28, height:28, borderRadius:6, background:meta.color+"15", display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0 }}>
                  <meta.icon size={14} color={meta.color} />
                </div>
                <span style={{ fontSize:13, fontWeight:500, color:"var(--text)", overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{r.title || type}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div style={{ flex:1, overflowY:"auto", padding:"24px 32px" }}>
        {selected ? (
          <div style={{ maxWidth:780 }}>
            <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:16 }}>
              <div style={{ width:36, height:36, borderRadius:8, background:getMeta(selected.resource_type||selected.type||"article").color+"15", display:"flex", alignItems:"center", justifyContent:"center" }}>
                {React.createElement(getMeta(selected.resource_type||selected.type||"article").icon, {size:18, color:getMeta(selected.resource_type||selected.type||"article").color})}
              </div>
              <h2 style={{ fontSize:18, fontWeight:700 }}>{selected.title || "资源"}</h2>
            </div>
            <div style={{ fontSize:14, lineHeight:1.8, color:"var(--text-secondary)" }}>
              {renderContent(selected.content || "")}
            </div>
          </div>
        ) : (
          <div style={{ display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", height:"100%", color:"var(--text-light)", gap:12 }}>
            <BookOpen size={48} />
            <p style={{fontSize:14}}>选择左侧资源或点击按钮生成新内容</p>
            <button onClick={()=>generateResource("article")} disabled={loading}
              style={{ padding:"8px 20px", borderRadius:"var(--radius)", background:"var(--primary)", color:"#fff", fontSize:14, fontWeight:500 }}>
              {loading ? "生成中..." : "生成教学文章"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
