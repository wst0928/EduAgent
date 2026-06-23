# EduAgent - 个性化学习多智能体系统

> Software Cup 2026 · A3赛道 · 基于大模型的个性化资源生成与学习多智能体系统开发

## 项目简介

EduAgent 是一个基于大模型技术的个性化学习多智能体系统。系统通过多智能体协同架构，为学生提供从画像构建、知识图谱生成、学习路径规划到多类型学习资源生成的全流程个性化学习服务。

### 核心功能

- **对话式画像构建**：通过自然语言对话自动抽取10维学生画像（专业、年级、知识基础、学习风格、认知风格、偏好难度、兴趣、易错点、学习节奏、学习动机）
- **多智能体协同资源生成**：6个专业Agent（用户画像、知识图谱、学习路径、资源生成、评估、协调）协同工作，生成教学文章、练习题、知识总结、学习指南、测验题等多类型资源
- **个性化学习路径规划**：根据画像和知识图谱，自动生成分阶段的学习路径和里程碑
- **知识图谱可视化**：构建学科知识结构，展示概念间的前置依赖关系
- **交互式测验系统**：自动生成测验题目，支持在线作答和自动判分

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite |
| 后端 | Python 3.12 + FastAPI |
| AI | DeepSeek Chat API + 预置课程知识库 |
| 存储 | 内存 + JSON文件持久化 |
| 构建 | pnpm（前端）/ pip（后端） |

### 多智能体架构

```
User Agent (用户画像)  ─┐
Knowledge Graph Agent  ─┤
Learning Path Agent   ─┤── Orchestrator (协调中心) ──→ 前端展示
Resource Agent        ─┤
Assessment Agent      ─┘
```

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- pnpm（或 npm）

### 安装与运行

```bash
# 1. 后端
cd backend
pip install -r requirements.txt

# 2. 配置API Key（可选，不配置也可使用离线课程库）
# 编辑 backend/.env 文件：
# LLM_API_KEY=your_api_key_here
# LLM_BASE_URL=https://api.deepseek.com/v1
# LLM_MODEL=deepseek-chat

# 3. 启动后端
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 4. 新终端 - 构建并启动前端
cd frontend
pnpm install
pnpm build
# 前端已通过后端静态文件服务加载，访问 http://127.0.0.1:8000
```

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── agents/           # 多智能体核心代码
│   │   │   ├── orchestrator.py        # 协调中心
│   │   │   ├── user_agent.py          # 用户画像Agent
│   │   │   ├── knowledge_graph_agent.py  # 知识图谱Agent
│   │   │   ├── learning_path_agent.py   # 学习路径Agent
│   │   │   ├── resource_generation_agent.py # 资源生成Agent
│   │   │   ├── assessment_agent.py     # 评估Agent
│   │   │   └── base_agent.py          # Agent基类
│   │   ├── api/              # REST API接口
│   │   ├── models/           # 数据模型
│   │   ├── services/         # LLM服务、内存服务
│   │   └── config.py         # 配置文件
│   ├── .env                  # API Key配置（已gitignore）
│   └── requirements.txt      # Python依赖
├── frontend/
│   ├── src/
│   │   ├── components/       # 前端组件
│   │   └── App.tsx           # 主应用
│   └── package.json
├── docs/                     # 文档
├── .gitignore
└── README.md
```

## API 接口

| 接口 | 方法 | 说明 |
|---|---|---|
| `/api/v1/chat` | POST | 对话接口，自动检测学习意图并触发工作流 |
| `/api/v1/resources/generate` | POST | 生成学习资源 |
| `/api/v1/resources` | GET | 获取所有资源 |
| `/api/v1/recommendations` | GET | 获取个性化推荐 |
| `/api/v1/quiz/generate` | POST | 生成测验 |
| `/api/v1/quiz/evaluate` | POST | 评估测验答案 |
| `/api/v1/seed/course` | POST | 初始化课程知识库 |
| `/api/v1/health` | GET | 健康检查 |

## 赛题功能对照

- [x] 对话式画像构建（≥6维，已实现10维）
- [x] 多智能体协同资源生成（≥5种类型）
- [x] 个性化学习路径规划与资源推送
- [ ] 智能辅导（加分项）
- [ ] 学习效果评估（加分项）

## 许可证

MIT
