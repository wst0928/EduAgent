import { type ReactNode } from "react";

type View = "chat" | "learning" | "resources" | "knowledge" | "quiz";

const navItems: { id: View; label: string; icon: string }[] = [
  { id: "chat", label: "学习对话", icon: "\u{1F4AC}" },
  { id: "learning", label: "学习路径", icon: "\u{1F9F0}" },
  { id: "resources", label: "学习资源", icon: "\u{1F4DA}" },
  { id: "knowledge", label: "知识图谱", icon: "\u{1F9E0}" },
  { id: "quiz", label: "交互测验", icon: "\u{1F4DD}" },
];

interface LayoutProps {
  children: ReactNode;
  currentView: View;
  onNavigate: (view: View) => void;
}

export default function Layout({ children, currentView, onNavigate }: LayoutProps) {
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <aside
        style={{
          width: 220,
          background: "var(--bg-sidebar)",
          color: "var(--text-on-dark)",
          display: "flex",
          flexDirection: "column",
          flexShrink: 0,
        }}
      >
        <div style={{ padding: "20px 16px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
          <h1 style={{ fontSize: 18, fontWeight: 700 }}>EduAgent</h1>
          <p style={{ fontSize: 12, color: "var(--text-light)", marginTop: 4 }}>个性化学习多智能体系统</p>
        </div>

        <nav style={{ flex: 1, padding: "12px 8px" }}>
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                width: "100%",
                padding: "10px 12px",
                borderRadius: "var(--radius)",
                background: currentView === item.id ? "rgba(255,255,255,0.12)" : "transparent",
                color: "var(--text-on-dark)",
                fontSize: 14,
                textAlign: "left",
                border: "none",
                marginBottom: 2,
              }}
            >
              <span style={{ fontSize: 18 }}>{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div style={{ padding: "12px 16px", borderTop: "1px solid rgba(255,255,255,0.1)", fontSize: 11, color: "var(--text-light)" }}>
          Software Cup 2026<br />基于大模型的个性化资源生成与学习多智能体系统
        </div>
      </aside>

      <main style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>
        {children}
      </main>
    </div>
  );
}
