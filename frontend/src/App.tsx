import { useState } from "react";
import Layout from "./components/Layout";
import ChatInterface from "./components/ChatInterface";
import LearningPath from "./components/LearningPath";
import ResourceViewer from "./components/ResourceViewer";
import KnowledgeGraph from "./components/KnowledgeGraph";
import QuizViewer from "./components/QuizViewer";

type View = "chat" | "learning" | "resources" | "knowledge" | "quiz";

interface AppState {
  currentView: View;
  userMessage: string;
  learningData: Record<string, any>;
}

export default function App() {
  const [state, setState] = useState<AppState>({
    currentView: "chat",
    userMessage: "",
    learningData: {},
  });

  const handleChatResponse = (response: Record<string, any>) => {
    const workflowResult = response.workflow_result || response;
    if (response.workflow === "start_learning" && workflowResult) {
      setState((prev) => ({
        ...prev,
        learningData: workflowResult,
        currentView: "learning",
      }));
    }
  };

  const navigateTo = (view: View) => {
    setState((prev) => ({ ...prev, currentView: view }));
  };

  const renderView = () => {
    switch (state.currentView) {
      case "chat":
        return <ChatInterface onResponse={handleChatResponse} />;
      case "learning":
        return (
          <LearningPath
            data={state.learningData}
            onStartResource={() => navigateTo("resources")}
            onBack={() => navigateTo("chat")}
          />
        );
      case "resources":
        return (
          <ResourceViewer
            topic={state.learningData?.topic || "当前主题"}
            onBack={() => navigateTo("learning")}
          />
        );
      case "quiz":
        return (
          <QuizViewer
            topic={state.learningData?.topic || "Python编程"}
            onBack={() => navigateTo("chat")}
          />
        );
      case "knowledge":
        return (
          <KnowledgeGraph
            data={state.learningData?.knowledge_graph}
            onBack={() => navigateTo("learning")}
          />
        );
      default:
        return <ChatInterface onResponse={handleChatResponse} />;
    }
  };

  return (
    <Layout currentView={state.currentView} onNavigate={navigateTo}>
      {renderView()}
    </Layout>
  );
}
