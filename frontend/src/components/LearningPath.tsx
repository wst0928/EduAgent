import { ArrowLeft, BookOpen, Clock, Award, Target } from "lucide-react";

interface Milestone {
  order: number;
  name: string;
  description: string;
  estimated_hours: number;
  difficulty: string;
  topics: string[];
  objectives: string[];
  recommended_resource_types: string[];
}

interface LearningPathProps {
  data: Record<string, any>;
  onStartResource: () => void;
  onBack: () => void;
}

export default function LearningPath({
  data,
  onStartResource,
  onBack,
}: LearningPathProps) {
  const milestones: Milestone[] = data?.learning_path?.milestones || [];
  const title = data?.learning_path?.title || data?.topic || "学习路径";
  const overview = data?.learning_path?.overview || "";
  const estimatedHours = data?.learning_path?.estimated_hours || 0;
  const tips: string[] = data?.learning_path?.learning_tips || [];
  const materials: string[] = data?.learning_path?.recommended_materials || [];

  const difficultyColor = (d: string) => {
    switch (d) {
      case "beginner":
        return "var(--success)";
      case "intermediate":
        return "var(--warning)";
      case "advanced":
        return "var(--error)";
      default:
        return "var(--text-secondary)";
    }
  };

  return (
    <div style={{ overflowY: "auto", flex: 1 }}>
      {/* Header */}
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
        <button
          onClick={onBack}
          style={{
            background: "none",
            color: "var(--text-secondary)",
            padding: 4,
            display: "flex",
          }}
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <h2 style={{ fontSize: 16, fontWeight: 600 }}>{title}</h2>
          <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            个性化学习路径 · 共约 {estimatedHours} 小时
          </p>
        </div>
      </div>

      <div
        style={{
          maxWidth: 720,
          margin: "0 auto",
          padding: "20px 24px",
          display: "flex",
          flexDirection: "column",
          gap: 20,
        }}
      >
        {/* Overview */}
        {overview && (
          <div
            style={{
              background: "var(--bg-card)",
              padding: 16,
              borderRadius: "var(--radius)",
              boxShadow: "var(--shadow)",
            }}
          >
            <h3
              style={{
                fontSize: 14,
                fontWeight: 600,
                marginBottom: 8,
                display: "flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <BookOpen size={16} /> 路径概览
            </h3>
            <p style={{ fontSize: 14, lineHeight: 1.6, color: "var(--text-secondary)" }}>
              {overview}
            </p>
          </div>
        )}

        {/* Milestones */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <h3
            style={{
              fontSize: 14,
              fontWeight: 600,
              display: "flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            <Target size={16} /> 学习里程碑
          </h3>

          {milestones.length === 0 && (
            <div
              style={{
                background: "var(--bg-card)",
                padding: 24,
                borderRadius: "var(--radius)",
                textAlign: "center",
                color: "var(--text-secondary)",
                fontSize: 14,
                boxShadow: "var(--shadow)",
              }}
            >
              请先在对话中设定一个学习目标，我将为你生成个性化学习路径。
            </div>
          )}

          {milestones.map((ms, i) => (
            <div
              key={i}
              style={{
                background: "var(--bg-card)",
                borderRadius: "var(--radius)",
                boxShadow: "var(--shadow)",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  padding: "12px 16px",
                  background: "var(--primary)",
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <span style={{ fontSize: 14, fontWeight: 600 }}>
                  阶段 {ms.order}: {ms.name}
                </span>
                <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                  <span
                    style={{
                      fontSize: 12,
                      padding: "2px 8px",
                      borderRadius: 10,
                      background: difficultyColor(ms.difficulty),
                      color: "#fff",
                    }}
                  >
                    {ms.difficulty === "beginner"
                      ? "入门"
                      : ms.difficulty === "intermediate"
                      ? "进阶"
                      : "高级"}
                  </span>
                  <span style={{ fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}>
                    <Clock size={12} /> {ms.estimated_hours}h
                  </span>
                </div>
              </div>
              <div style={{ padding: 16 }}>
                <p
                  style={{
                    fontSize: 13,
                    color: "var(--text-secondary)",
                    lineHeight: 1.5,
                    marginBottom: 12,
                  }}
                >
                  {ms.description}
                </p>
                {ms.topics.length > 0 && (
                  <div style={{ marginBottom: 12 }}>
                    <p
                      style={{
                        fontSize: 12,
                        fontWeight: 600,
                        color: "var(--text-secondary)",
                        marginBottom: 6,
                      }}
                    >
                      涵盖知识点：
                    </p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                      {ms.topics.map((t, j) => (
                        <span
                          key={j}
                          style={{
                            padding: "2px 8px",
                            borderRadius: 10,
                            background: "var(--bg)",
                            fontSize: 12,
                            color: "var(--primary)",
                          }}
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {ms.objectives.length > 0 && (
                  <div>
                    <p
                      style={{
                        fontSize: 12,
                        fontWeight: 600,
                        color: "var(--text-secondary)",
                        marginBottom: 4,
                      }}
                    >
                      学习目标：
                    </p>
                    {ms.objectives.map((obj, j) => (
                      <div
                        key={j}
                        style={{
                          display: "flex",
                          gap: 6,
                          alignItems: "flex-start",
                          fontSize: 13,
                          color: "var(--text-secondary)",
                          marginBottom: 2,
                        }}
                      >
                        <span style={{ color: "var(--success)" }}>{"\u2713"}</span>
                        <span>{obj}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Learning Tips */}
        {tips.length > 0 && (
          <div
            style={{
              background: "var(--bg-card)",
              padding: 16,
              borderRadius: "var(--radius)",
              boxShadow: "var(--shadow)",
            }}
          >
            <h3
              style={{
                fontSize: 14,
                fontWeight: 600,
                marginBottom: 8,
                display: "flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <Award size={16} /> 学习建议
            </h3>
            {tips.map((tip, i) => (
              <p
                key={i}
                style={{
                  fontSize: 13,
                  color: "var(--text-secondary)",
                  lineHeight: 1.5,
                  marginBottom: 4,
                  paddingLeft: 12,
                  borderLeft: "2px solid var(--primary-light)",
                }}
              >
                {tip}
              </p>
            ))}
          </div>
        )}

        {/* Recommended Materials */}
        {materials.length > 0 && (
          <div
            style={{
              background: "var(--bg-card)",
              padding: 16,
              borderRadius: "var(--radius)",
              boxShadow: "var(--shadow)",
            }}
          >
            <h3
              style={{
                fontSize: 14,
                fontWeight: 600,
                marginBottom: 8,
                display: "flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <BookOpen size={16} /> 推荐资料
            </h3>
            {materials.map((mat, i) => (
              <p
                key={i}
                style={{
                  fontSize: 13,
                  color: "var(--text-secondary)",
                  marginBottom: 4,
                }}
              >
                {"\u2022"} {mat}
              </p>
            ))}
          </div>
        )}

        {/* Action buttons */}
        <div style={{ display: "flex", gap: 8 }}>
          <button
            onClick={onStartResource}
            style={{
              flex: 1,
              padding: "10px 20px",
              borderRadius: "var(--radius)",
              background: "var(--primary)",
              color: "#fff",
              fontSize: 14,
              fontWeight: 600,
            }}
          >
            查看学习资源
          </button>
        </div>
      </div>
    </div>
  );
}
