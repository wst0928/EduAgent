import { useState, useRef, useEffect } from "react";
import { Bot, Loader2, Send, User } from "lucide-react";

interface ChatInterfaceProps {
  onResponse: (data: Record<string, any>) => void;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
}

const API_BASE = "/api/v1";

export default function ChatInterface({ onResponse }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "你好！我是 EduAgent，个性化学习助手。\n\n我可以帮你：\n- 设定学习目标：告诉我你想学什么，我来规划学习路径\n- 生成学习资源：根据你的水平和偏好生成个性化内容\n- 知识图谱：构建学科知识结构\n- 测验评估：生成测验并评估掌握程度\n\n试试告诉我你想学什么？ 比如「我想学Python」或「想了解机器学习」。",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const msg = input.trim();
    setInput("");
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: msg }, { role: "assistant", content: "", streaming: true }]);

    try {
      const res = await fetch(API_BASE + "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "default", message: msg, workflow: "chat" }),
      });
      const data = await res.json();
      const reply = data.reply || "好的，让我为你准备学习内容...";

      setMessages((prev) => {
        const u = [...prev];
        for (let i = u.length - 1; i >= 0; i--) { if (u[i].role === "assistant") { u[i] = { role: "assistant", content: reply, streaming: false }; break; } }
        return u;
      });

      if (data.workflow === "start_learning" || data.workflow_result) {
        setTimeout(() => onResponse(data), 600);
      }
    } catch {
      setMessages((prev) => {
        const u = [...prev];
        for (let i = u.length - 1; i >= 0; i--) { if (u[i].role === "assistant") { u[i] = { role: "assistant", content: "连接服务器时出现问题，请确保后端服务已启动。", streaming: false }; break; } }
        return u;
      });
    } finally {
      setLoading(false);
    }
  };

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
      if (line.startsWith("- ")) { els.push(<p key={"l"+i} style={{marginBottom:2,fontSize:14,lineHeight:1.6,paddingLeft:12}}><span dangerouslySetInnerHTML={{__html:line.slice(2)}} /></p>); continue; }
      els.push(<p key={"p"+i} style={{marginBottom:4,fontSize:14,lineHeight:1.6}}>{line}</p>);
    }
    if (inCode && codeBuf.length) els.push(<pre key={"ce"} style={{background:"#1e1e2e",color:"#cdd6f4",borderRadius:8,padding:"12px 16px",overflow:"auto",fontSize:13,lineHeight:1.5,fontFamily:"monospace"}}><code>{codeBuf.join("\n")}</code></pre>);
    return els;
  };

  return (
    <div style={{display:"flex",flexDirection:"column",height:"100%",maxWidth:800,margin:"0 auto",width:"100%"}}>
      <div style={{padding:"16px 24px",borderBottom:"1px solid var(--border)",background:"var(--bg-card)"}}>
        <h2 style={{fontSize:16,fontWeight:600}}>学习对话</h2>
        <p style={{fontSize:13,color:"var(--text-secondary)",marginTop:2}}>与 EduAgent 智能体对话</p>
      </div>
      <div style={{flex:1,overflowY:"auto",padding:"16px 24px",display:"flex",flexDirection:"column",gap:12}}>
        {messages.map((msg, i) => (
          <div key={i} style={{display:"flex",gap:10,alignItems:"flex-start",flexDirection:msg.role==="user"?"row-reverse":"row"}}>
            <div style={{width:32,height:32,borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center",background:msg.role==="user"?"var(--primary)":"var(--bg-sidebar)",color:"#fff",flexShrink:0}}>
              {msg.role==="user"?<User size={16}/>:<Bot size={16}/>}
            </div>
            <div style={{maxWidth:"75%",padding:"10px 14px",borderRadius:12,background:msg.role==="user"?"var(--primary)":"var(--bg-card)",color:msg.role==="user"?"#fff":"var(--text)",fontSize:14,lineHeight:1.6,boxShadow:"var(--shadow)"}}>
              {msg.role==="assistant"?renderContent(msg.content):msg.content}
              {msg.streaming&&<span style={{display:"inline-block",animation:"blink 0.8s infinite",marginLeft:2}}>|</span>}
            </div>
          </div>
        ))}
        <div ref={endRef}/>
      </div>
      <div style={{padding:"12px 24px 20px",borderTop:"1px solid var(--border)",background:"var(--bg-card)"}}>
        <div style={{display:"flex",gap:8,background:"var(--bg)",borderRadius:"var(--radius)",border:"1px solid var(--border)",padding:"4px 4px 4px 16px"}}>
          <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();sendMessage();}}} placeholder="输入你想学习的内容..." disabled={loading}
            style={{flex:1,border:"none",background:"transparent",padding:"8px 0",fontSize:14,color:"var(--text)"}}/>
          <button onClick={sendMessage} disabled={loading||!input.trim()}
            style={{padding:"8px 16px",borderRadius:"var(--radius)",background:loading||!input.trim()?"var(--border)":"var(--primary)",color:loading||!input.trim()?"var(--text-light)":"#fff",display:"flex",alignItems:"center",gap:6,fontSize:14,fontWeight:500}}>
            {loading?<Loader2 size={16} style={{animation:"spin 1s linear infinite"}}/>:<Send size={16}/>}
            发送
          </button>
        </div>
      </div>
      <style>{`@keyframes blink{0\%,100\%{opacity:1}50\%{opacity:0}}@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}`}</style>
    </div>
  );
}
