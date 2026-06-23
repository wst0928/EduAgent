import { ArrowLeft, Network, Info } from "lucide-react";

interface NodeData {
  id: string;
  name: string;
  description: string;
  node_type: string;
  difficulty: number;
  estimated_hours: number;
}

interface EdgeData {
  source_id: string;
  target_id: string;
  relation_type: string;
  description: string;
}

interface KnowledgeGraphProps {
  data: { node_count?: number; edge_count?: number; nodes?: NodeData[]; edges?: EdgeData[] };
  onBack: () => void;
}

const relationLabels: Record<string, string> = {
  prerequisite: "前置知识",
  composed_of: "组成",
  related_to: "相关",
  teaches: "教学",
};

const typeColors: Record<string, string> = {
  subject: "#4f46e5",
  topic: "#0891b2",
  concept: "#059669",
  prerequisite: "#d97706",
  skill: "#7c3aed",
};

export default function KnowledgeGraph({ data, onBack }: KnowledgeGraphProps) {
  const nodes = data?.nodes || [];
  const edges = data?.edges || [];

  return (
    <div style={{ overflowY: "auto", flex: 1 }}>
      <div
        style={{
          padding: "16px 24px",
          borderBottom: "1px solid var(--border)",
          background: "var(--bg-card)",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <button onClick={onBack} style={{ background: "none", color: "var(--text-secondary)", padding: 4, display: "flex" }}>
          <ArrowLeft size={20} />
        </button>
        <div>
          <h2 style={{ fontSize: 16, fontWeight: 600 }}>知识图谱</h2>
          <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            {data?.node_count || 0} 个知识点 · {data?.edge_count || 0} 条关系
          </p>
        </div>
      </div>

      {nodes.length === 0 ? (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: 300,
            color: "var(--text-light)",
            gap: 8,
          }}
        >
          <Network size={40} />
          <p style={{ fontSize: 14 }}>请先在对话中设定学习主题，系统将自动构建知识图谱。</p>
        </div>
      ) : (
        <div style={{ maxWidth: 800, margin: "0 auto", padding: "20px 24px", display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Visual representation */}
          <div
            style={{
              background: "var(--bg-card)",
              borderRadius: "var(--radius)",
              boxShadow: "var(--shadow)",
              padding: 24,
            }}
          >
            <div
              style={{
                position: "relative",
                minHeight: 400,
                display: "flex",
                flexDirection: "column",
                gap: 20,
              }}
            >
              {/* Tree layout: group by type */}
              {["subject", "topic", "concept", "prerequisite", "skill"].map((type) => {
                const typeNodes = nodes.filter((n) => n.node_type === type);
                if (typeNodes.length === 0) return null;
                return (
                  <div key={type}>
                    <div
                      style={{
                        fontSize: 12,
                        fontWeight: 600,
                        color: typeColors[type] || "var(--text-secondary)",
                        marginBottom: 8,
                        paddingLeft: 8,
                        borderLeft: `3px solid ${typeColors[type] || "var(--text-secondary)"}`,
                      }}
                    >
                      {type === "subject" ? "学科" : type === "topic" ? "主题" : type === "concept" ? "概念" : type === "prerequisite" ? "前置知识" : "技能"}
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      {typeNodes.map((node) => (
                        <div
                          key={node.id}
                          style={{
                            padding: "8px 12px",
                            borderRadius: "var(--radius)",
                            background: `${typeColors[type] || "var(--primary)"}10`,
                            border: `1px solid ${typeColors[type] || "var(--primary)"}30`,
                            fontSize: 13,
                            fontWeight: 500,
                          }}
                        >
                          {node.name}
                          <div style={{ fontSize: 11, color: "var(--text-light)", fontWeight: 400, marginTop: 4 }}>
                            难度 {node.difficulty}/5 · {node.estimated_hours}h
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Edge list */}
          {edges.length > 0 && (
            <div
              style={{
                background: "var(--bg-card)",
                borderRadius: "var(--radius)",
                boxShadow: "var(--shadow)",
                padding: 16,
              }}
            >
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, display: "flex", alignItems: "center", gap: 6 }}>
                <Info size={16} /> 关系列表
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {edges.map((edge, i) => {
                  const source = nodes.find((n) => n.id === edge.source_id);
                  const target = nodes.find((n) => n.id === edge.target_id);
                  return (
                    <div
                      key={i}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        fontSize: 13,
                        color: "var(--text-secondary)",
                      }}
                    >
                      <span style={{ fontWeight: 500, color: "var(--text)" }}>
                        {source?.name || edge.source_id}
                      </span>
                      <span
                        style={{
                          padding: "1px 6px",
                          borderRadius: 8,
                          background: "var(--bg)",
                          fontSize: 11,
                          color: "var(--primary)",
                        }}
                      >
                        {relationLabels[edge.relation_type] || edge.relation_type}
                      </span>
                      <span style={{ fontWeight: 500, color: "var(--text)" }}>
                        {target?.name || edge.target_id}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
