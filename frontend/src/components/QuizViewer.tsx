import { useState, useEffect } from "react";
import { ArrowLeft, CheckCircle2, XCircle, Award, Loader2 } from "lucide-react";

interface Question {
  question: string;
  options: string[];
  difficulty?: number;
}

interface QuizResult {
  score: number;
  correct: number;
  total: number;
  passed: boolean;
  feedback: string;
  results: {
    question_num: number;
    question: string;
    user_answer: string;
    correct_answer: string;
    is_correct: boolean;
    explanation: string;
  }[];
}

interface QuizData {
  resource_id: string;
  title: string;
  questions: Question[];
}

interface QuizViewerProps {
  quizId?: string;
  topic?: string;
  onBack: () => void;
}

const API_BASE = "/api/v1";

export default function QuizViewer({ quizId: initialQuizId, topic = "Python编程", onBack }: QuizViewerProps) {
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [answers, setAnswers] = useState<number[]>([]);
  const [currentQ, setCurrentQ] = useState(0);
  const [result, setResult] = useState<QuizResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    generateQuiz();
  }, []);

  const generateQuiz = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/quiz/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "default",
          topic,
          difficulty: "beginner",
          num_questions: 5,
        }),
      });
      const data = await res.json();
      const quiz = data.quiz;
      // Strip correct_index before storing in state
      const cleanQuestions = (quiz.questions || []).map((q: any) => ({
        question: q.question,
        options: q.options,
        difficulty: q.difficulty,
      }));
      setQuizData({
        resource_id: data.resource_id,
        title: quiz.title || `${topic} 测验`,
        questions: cleanQuestions,
      });
      setAnswers(new Array(cleanQuestions.length).fill(-1));
    } catch (e) {
      // Use demo data if API fails
      setQuizData({
        resource_id: "demo",
        title: `${topic} 基础测验`,
        questions: [
          { question: "Python中`len([1,2,3])`的值是？", options: ["2", "3", "4", "报错"] },
          { question: "定义函数的正确关键字是？", options: ["function", "def", "define", "func"] },
          { question: "列表推导式`[x*2 for x in range(3)]`的结果？", options: ["[0,2,4]", "[0,2,6]", "[1,2,3]", "[2,4,6]"] },
          { question: "以下哪个是合法的变量名？", options: ["2name", "my_name", "my-name", "class"] },
          { question: "try语句的作用是？", options: ["定义函数", "处理异常", "创建循环", "导入模块"] },
        ],
      });
      setAnswers(new Array(5).fill(-1));
    } finally {
      setLoading(false);
    }
  };

  const submitQuiz = async () => {
    if (!quizData) return;
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/quiz/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          quiz_id: quizData.resource_id,
          answers,
        }),
      });
      const data = await res.json();
      setResult(data);
    } catch {
      // Demo result
      const correctCount = answers.filter((a, i) => a === [1, 1, 0, 1, 1][i]).length;
      setResult({
        score: Math.round((correctCount / answers.length) * 100),
        correct: correctCount,
        total: answers.length,
        passed: correctCount >= 3,
        feedback: correctCount >= 3 ? "不错！基础知识掌握得比较扎实。" : "需要加强练习，建议复习基础语法部分。",
        results: answers.map((a, i) => ({
          question_num: i + 1,
          question: quizData.questions[i]?.question || "",
          user_answer: quizData.questions[i]?.options[a] || "未作答",
          correct_answer: quizData.questions[i]?.options[[1, 1, 0, 1, 1][i]] || "",
          is_correct: a === [1, 1, 0, 1, 1][i],
          explanation: "参考答案如上。",
        })),
      });
    } finally {
      setSubmitting(false);
    }
  };

  const selectAnswer = (qIndex: number, optIndex: number) => {
    const newAnswers = [...answers];
    newAnswers[qIndex] = optIndex;
    setAnswers(newAnswers);
  };

  const allAnswered = answers.every((a) => a >= 0);

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", flexDirection: "column", gap: 12, color: "var(--text-secondary)" }}>
        <Loader2 size={32} style={{ animation: "spin 1s linear infinite" }} />
        <p>正在生成测验题目...</p>
      </div>
    );
  }

  if (result) {
    return (
      <div style={{ overflowY: "auto", flex: 1 }}>
        <div style={{ maxWidth: 600, margin: "0 auto", padding: "24px" }}>
          <div style={{ background: "var(--bg-card)", borderRadius: "var(--radius)", boxShadow: "var(--shadow-lg)", padding: 32, textAlign: "center", marginBottom: 20 }}>
            <Award size={48} color={result.passed ? "var(--success)" : "var(--warning)"} style={{ marginBottom: 12 }} />
            <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>
              {result.passed ? "恭喜通过！" : "再接再厉"}
            </h2>
            <div style={{ fontSize: 48, fontWeight: 800, color: result.passed ? "var(--success)" : "var(--error)", marginBottom: 8 }}>
              {result.score}分
            </div>
            <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
              正确 {result.correct}/{result.total} 题
            </p>
          </div>

          {result.results.map((r, i) => (
            <div key={i} style={{ background: "var(--bg-card)", borderRadius: "var(--radius)", boxShadow: "var(--shadow)", padding: 16, marginBottom: 12 }}>
              <div style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 8 }}>
                {r.is_correct ? <CheckCircle2 size={18} color="var(--success)" style={{ flexShrink: 0, marginTop: 2 }} /> : <XCircle size={18} color="var(--error)" style={{ flexShrink: 0, marginTop: 2 }} />}
                <div>
                  <p style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>第{r.question_num}题: {r.question}</p>
                  <p style={{ fontSize: 13, color: r.is_correct ? "var(--success)" : "var(--error)", marginBottom: 2 }}>
                    你的答案: {r.user_answer}
                  </p>
                  {!r.is_correct && (
                    <p style={{ fontSize: 13, color: "var(--success)" }}>
                      正确答案: {r.correct_answer}
                    </p>
                  )}
                  <p style={{ fontSize: 12, color: "var(--text-light)", marginTop: 4 }}>{r.explanation}</p>
                </div>
              </div>
            </div>
          ))}

          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={() => { setResult(null); setAnswers(new Array(quizData?.questions.length || 5).fill(-1)); setCurrentQ(0); generateQuiz(); }}
              style={{ flex: 1, padding: "10px 20px", borderRadius: "var(--radius)", background: "var(--bg-card)", color: "var(--text)", fontSize: 14, fontWeight: 500, border: "1px solid var(--border)" }}>
              重新测验
            </button>
            <button onClick={onBack}
              style={{ flex: 1, padding: "10px 20px", borderRadius: "var(--radius)", background: "var(--primary)", color: "#fff", fontSize: 14, fontWeight: 500, border: "none" }}>
              返回
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!quizData) return null;

  const q = quizData.questions[currentQ];

  return (
    <div style={{ overflowY: "auto", flex: 1 }}>
      <div style={{ padding: "16px 24px", borderBottom: "1px solid var(--border)", background: "var(--bg-card)", display: "flex", alignItems: "center", gap: 12 }}>
        <button onClick={onBack} style={{ background: "none", color: "var(--text-secondary)", padding: 4, display: "flex" }}>
          <ArrowLeft size={20} />
        </button>
        <div>
          <h2 style={{ fontSize: 16, fontWeight: 600 }}>{quizData.title}</h2>
          <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            第 {currentQ + 1}/{quizData.questions.length} 题 · {answers.filter((a) => a >= 0).length} 题已答
          </p>
        </div>
      </div>

      <div style={{ maxWidth: 600, margin: "0 auto", padding: "24px" }}>
        {/* Progress bar */}
        <div style={{ display: "flex", gap: 4, marginBottom: 24 }}>
          {quizData.questions.map((_, i) => (
            <div key={i} style={{
              flex: 1, height: 4, borderRadius: 2,
              background: i === currentQ ? "var(--primary)" : answers[i] >= 0 ? "var(--success)" : "var(--border)",
              cursor: "pointer",
            }} onClick={() => setCurrentQ(i)} />
          ))}
        </div>

        {/* Question */}
        <div style={{ background: "var(--bg-card)", borderRadius: "var(--radius)", boxShadow: "var(--shadow)", padding: 24 }}>
          <p style={{ fontSize: 12, color: "var(--text-light)", marginBottom: 8, textTransform: "uppercase" }}>
            第 {currentQ + 1} 题
          </p>
          <h3 style={{ fontSize: 16, fontWeight: 600, lineHeight: 1.5, marginBottom: 20 }}>
            {q.question}
          </h3>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {q.options.map((opt, oi) => (
              <button key={oi} onClick={() => selectAnswer(currentQ, oi)}
                style={{
                  padding: "12px 16px", borderRadius: "var(--radius)", border: answers[currentQ] === oi ? "2px solid var(--primary)" : "1px solid var(--border)",
                  background: answers[currentQ] === oi ? "var(--primary)" : "var(--bg-card)",
                  color: answers[currentQ] === oi ? "#fff" : "var(--text)",
                  fontSize: 14, textAlign: "left", cursor: "pointer",
                  display: "flex", alignItems: "center", gap: 10,
                  transition: "all 0.15s",
                }}
                onMouseEnter={(e) => { if (answers[currentQ] !== oi) e.currentTarget.style.borderColor = "var(--primary-light)"; }}
                onMouseLeave={(e) => { if (answers[currentQ] !== oi) e.currentTarget.style.borderColor = "var(--border)"; }}
              >
                <span style={{
                  width: 24, height: 24, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
                  background: answers[currentQ] === oi ? "rgba(255,255,255,0.2)" : "var(--bg)",
                  fontSize: 12, fontWeight: 600, flexShrink: 0,
                }}>
                  {String.fromCharCode(65 + oi)}
                </span>
                {opt}
              </button>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 20, gap: 8 }}>
          <button onClick={() => setCurrentQ(Math.max(0, currentQ - 1))} disabled={currentQ === 0}
            style={{ padding: "10px 20px", borderRadius: "var(--radius)", background: "var(--bg-card)", color: "var(--text)", fontSize: 14, border: "1px solid var(--border)", opacity: currentQ === 0 ? 0.5 : 1 }}>
            上一题
          </button>

          {currentQ < quizData.questions.length - 1 ? (
            <button onClick={() => setCurrentQ(currentQ + 1)}
              style={{ padding: "10px 20px", borderRadius: "var(--radius)", background: "var(--primary)", color: "#fff", fontSize: 14, border: "none" }}>
              下一题
            </button>
          ) : (
            <button onClick={submitQuiz} disabled={!allAnswered || submitting}
              style={{ padding: "10px 24px", borderRadius: "var(--radius)", background: !allAnswered ? "var(--border)" : "var(--success)", color: !allAnswered ? "var(--text-light)" : "#fff", fontSize: 14, fontWeight: 600, border: "none", display: "flex", alignItems: "center", gap: 6 }}>
              {submitting ? <Loader2 size={16} style={{ animation: "spin 1s linear infinite" }} /> : <CheckCircle2 size={16} />}
              交卷
            </button>
          )}
        </div>
      </div>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
