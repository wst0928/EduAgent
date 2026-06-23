# EduAgent 系统架构文档

## 1. 总体架构

EduAgent 采用**微服务 + 多智能体**架构，通过 FastAPI 作为 API 网关，协调多个专业 Agent 的协作。

### 架构图

```
┌─────────────────────────────────────────────────────┐
│                   用户界面 (React)                     │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/JSON
                     ▼
┌─────────────────────────────────────────────────────┐
│               API Gateway (FastAPI)                   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              Orchestrator (协调中心)                   │
│                                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ User     │ │ Know-    │ │ Resource │ │ Learning │ │
│  │ Agent    │ │ ledge    │ │ Gen.     │ │ Path     │ │
│  │          │ │ Graph    │ │ Agent    │ │ Agent    │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│  ┌──────────────────────────────────────────────────┐ │
│  │              Assessment Agent                     │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
  ┌──────────────┐    ┌────────────────┐
  │  LLM Service │    │  Memory        │
  │  (OpenAI)    │    │  Service       │
  └──────────────┘    │  (JSON/DB)     │
                      └────────────────┘
```

## 2. 智能体设计

### 2.1 BaseAgent (基类)

所有 Agent 继承自 BaseAgent，提供：
- LLM 聊天和结构输出封装
- 存储服务访问
- 会话上下文管理

### 2.2 UserAgent (用户画像代理)

**输入**: 用户消息、当前用户画像
**输出**: 用户意图、更新后的画像、学习目标

工作流程：
1. 接收用户消息
2. 调用 LLM 分析意图（set_goal/ask_question/request_resource/other）
3. 提取或更新用户画像（已有知识、兴趣、学习风格）
4. 返回意图结果和回复

### 2.3 KnowledgeGraphAgent (知识图谱代理)

**输入**: 学习主题
**输出**: 知识图谱（节点+边）

工作流程：
1. 接收学习主题
2. 调用 LLM 生成领域知识图谱
3. 解析为 KnowledgeGraph 结构（节点、边、关系类型）
4. 持久化存储
5. 支持前置知识查询和主题分解

### 2.4 ResourceGenerationAgent (资源生成代理)

**输入**: 主题、资源类型、用户画像、难度
**输出**: 生成的 LearningResource

支持资源类型：
- article: 教学文章
- summary: 知识总结
- quiz: 测验题目
- exercise: 练习题
- code_example: 代码示例
- study_guide: 学习指南
- flashcard: 闪卡
- mind_map: 思维导图

### 2.5 LearningPathAgent (学习路径代理)

**输入**: 学习主题、用户画像、时间约束
**输出**: 结构化学习路径（里程碑）

支持：
- 路径规划（优先级、前置依赖）
- 进度追踪
- 动态调整（根据反馈）

### 2.6 AssessmentAgent (评估代理)

**输入**: 测验主题或用户答案
**输出**: 测验题目或评估结果

能力：
- 测验生成（选择题）
- 答案评估（计分、反馈）
- 薄弱环节分析
- 闪卡生成

### 2.7 Orchestrator (协调器)

负责：
- 路由用户请求到适当的 Agent
- 编排多步骤工作流
- 聚合多个 Agent 的结果

## 3. 工作流

### 3.1 对话工作流
User → Orchestrator → UserAgent(分析意图) → Orchestrator → User

### 3.2 开始学习工作流
User("我想学习Python") → Orchestrator → UserAgent(提取目标)
                                       → KnowledgeGraphAgent(构建图谱)
                                       → LearningPathAgent(规划路径)
                                       → ResourceGenerationAgent(生成资源)
                                       → Orchestrator(聚合) → User

### 3.3 资源生成工作流
User → Orchestrator → ResourceGenerationAgent → User

### 3.4 评估工作流
User → Orchestrator → AssessmentAgent(生成测验) → User(作答)
     → Orchestrator → AssessmentAgent(评估) → User

## 4. 数据模型

### User
- profile: name, existing_knowledge, learning_style, interests
- goals: 学习目标列表
- learning_progress: 各主题进度

### KnowledgeGraph
- nodes: 知识节点(概念/主题/技能)
- edges: 关系边(前置/组成/相关)

### LearningResource
- 类型: article/summary/quiz/exercise/code_example/...
- 内容: LLM 生成的文本
- 元数据: 难度、阅读时间、关联知识点

## 5. 技术决策

### 为什么用 LLM Agent 模式？
- 每个 Agent 专注于单一职责，易于维护和扩展
- LLM 的自然语言理解能力使 Agent 能灵活处理用户意图
- 结构化的输出格式保证系统可靠性

### 为什么 Agent 间不直接通信？
- 通过 Orchestrator 统一调度，避免 Agent 间的耦合
- 便于监控、日志和调试
- 可以灵活组合工作流
