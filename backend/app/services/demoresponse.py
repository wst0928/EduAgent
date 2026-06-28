"""离线演示模式：根据用户输入的主题动态生成示范回复，支持多个学科"""
import json

# ========== 预置课程知识库 ==========
COURSE_TOPICS = {
    "python": {
        "name": "Python编程",
        "nodes": [
            {"id": "py_intro", "name": "Python介绍", "description": "Python的基本概念和发展历史", "node_type": "topic", "difficulty": 1, "tags": ["入门"], "estimated_hours": 2},
            {"id": "py_basics", "name": "基础语法", "description": "变量、数据类型、运算符", "node_type": "topic", "difficulty": 1, "tags": ["基础"], "estimated_hours": 4},
            {"id": "py_control", "name": "流程控制", "description": "条件判断、循环语句", "node_type": "concept", "difficulty": 2, "tags": ["核心"], "estimated_hours": 3},
            {"id": "py_func", "name": "函数与模块", "description": "函数定义、参数传递、模块导入", "node_type": "concept", "difficulty": 2, "tags": ["核心"], "estimated_hours": 4},
            {"id": "py_data", "name": "数据结构", "description": "列表、字典、元组、集合", "node_type": "concept", "difficulty": 2, "tags": ["核心"], "estimated_hours": 3},
            {"id": "py_oop", "name": "面向对象编程", "description": "类、继承、多态", "node_type": "topic", "difficulty": 3, "tags": ["进阶"], "estimated_hours": 5},
            {"id": "py_libs", "name": "常用库", "description": "NumPy, Pandas, Matplotlib", "node_type": "skill", "difficulty": 3, "tags": ["实践"], "estimated_hours": 6},
            {"id": "math_basic", "name": "数学基础", "description": "基本数学运算、逻辑思维", "node_type": "prerequisite", "difficulty": 1, "tags": ["前置"], "estimated_hours": 1},
        ],
        "edges": [
            {"source_id": "math_basic", "target_id": "py_intro", "relation_type": "prerequisite", "weight": 1.0, "description": ""},
            {"source_id": "py_intro", "target_id": "py_basics", "relation_type": "prerequisite", "weight": 1.0, "description": ""},
            {"source_id": "py_basics", "target_id": "py_control", "relation_type": "prerequisite", "weight": 1.0, "description": ""},
            {"source_id": "py_control", "target_id": "py_func", "relation_type": "prerequisite", "weight": 1.0, "description": ""},
            {"source_id": "py_func", "target_id": "py_data", "relation_type": "prerequisite", "weight": 1.0, "description": ""},
            {"source_id": "py_data", "target_id": "py_oop", "relation_type": "prerequisite", "weight": 1.0, "description": ""},
            {"source_id": "py_oop", "target_id": "py_libs", "relation_type": "prerequisite", "weight": 1.0, "description": ""},
        ],
        "milestones": [
            {"order": 1, "name": "Python基础入门", "description": "学习Python的基本语法、变量、数据类型和运算符，搭建开发环境。", "estimated_hours": 6, "difficulty": "beginner", "topics": ["环境搭建", "变量与类型", "输入输出"], "objectives": ["能编写第一个Python程序", "理解基本数据类型"], "recommended_resource_types": ["article", "exercise"]},
            {"order": 2, "name": "流程控制与函数", "description": "掌握条件判断、循环结构和函数定义，培养编程逻辑思维。", "estimated_hours": 6, "difficulty": "beginner", "topics": ["if语句", "for/while循环", "函数定义"], "objectives": ["能使用条件语句控制程序流程", "能编写带参数的函数"], "recommended_resource_types": ["article", "exercise", "quiz"]},
            {"order": 3, "name": "数据结构与模块化", "description": "学习列表、字典等核心数据结构，理解模块化编程思想。", "estimated_hours": 8, "difficulty": "intermediate", "topics": ["列表与字典", "文件操作", "模块导入"], "objectives": ["能使用列表和字典组织数据", "能读写文件"], "recommended_resource_types": ["article", "code_example", "exercise"]},
            {"order": 4, "name": "面向对象与项目实践", "description": "掌握面向对象编程，完成一个小型项目实战演练。", "estimated_hours": 8, "difficulty": "intermediate", "topics": ["类与对象", "继承", "综合项目"], "objectives": ["能设计简单的类", "完成一个Python小项目"], "recommended_resource_types": ["article", "code_example", "study_guide"]},
        ],
        "total_hours": 28,
        "overview": "本路径将从零开始带领你掌握Python编程，涵盖基础语法、数据结构、函数、面向对象编程和常用库的使用。共分为4个阶段，循序渐进。",
        "tips": ["多动手写代码，每学一个概念就编写小程序验证", "善用官方文档和在线资源", "加入编程社区，遇到问题主动搜索和交流"],
        "materials": ["Python官方文档", "《Python编程从入门到实践》", "LeetCode编程练习平台"],
        "articles": ["# Python编程基础\n\nPython是一种高级、解释型、面向对象的编程语言，由Guido van Rossum于1991年创建。它以简洁的语法和强大的功能著称。\n\n## 快速开始\n安装Python后，打开终端输入 `python --version` 验证安装。\n\n### 你的第一个程序\n```python\nprint(\"Hello, World!\")\n```\n\n### 变量和数据类型\n```python\nname = \"小明\"       # 字符串\nage = 18            # 整数\nheight = 1.75       # 浮点数\nis_student = True   # 布尔值\n```", """# Python基础语法详解

## 变量与数据类型
Python是动态类型语言，变量不需要声明类型。
基本类型：str、int、float、bool、list

## 流程控制
if/elif/else 条件判断；for/while 循环

## 函数定义
def greet(name): return f"Hello, {name}"

## 常用数据结构
列表(list)、元组(tuple)、字典(dict)、集合(set)
""", """# Python面向对象编程

## 类与对象
class Student:
    def __init__(self, name, age):
        self.name = name; self.age = age

## 继承
子类继承父类的方法和属性。

## 魔术方法
__str__、__len__、__eq__ 等让类更强大。
""", """# NumPy入门

## 创建数组
import numpy as np
arr = np.array([1,2,3,4,5])
zeros = np.zeros((3,4))

## 数组运算
a = np.array([1,2,3]); b = np.array([4,5,6])
print(a + b)  # [5 7 9]
print(np.dot(a, b))  # 32
""", """# Pandas数据分析

## 创建DataFrame
import pandas as pd
df = pd.DataFrame({"name": ["A","B","C"], "score": [85,92,78]})

## 数据操作
print(df.head())
print(df.describe())
high = df[df["score"] > 80]
"""],
    },
    "机器学习": {
        "name": "机器学习",
        "nodes": [
            {"id": "ml_intro", "name": "机器学习概论", "description": "机器学习的基本概念、分类和应用领域", "node_type": "topic", "difficulty": 1, "tags": ["入门"], "estimated_hours": 3},
            {"id": "ml_math", "name": "数学基础", "description": "线性代数、概率统计、微积分基础", "node_type": "prerequisite", "difficulty": 2, "tags": ["前置"], "estimated_hours": 8},
            {"id": "ml_supervised", "name": "监督学习", "description": "线性回归、逻辑回归、决策树、SVM", "node_type": "topic", "difficulty": 2, "tags": ["核心"], "estimated_hours": 10},
            {"id": "ml_unsupervised", "name": "无监督学习", "description": "K-Means聚类、PCA降维、DBSCAN", "node_type": "topic", "difficulty": 3, "tags": ["核心"], "estimated_hours": 6},
            {"id": "ml_deep", "name": "深度学习入门", "description": "神经网络基础、CNN、RNN", "node_type": "topic", "difficulty": 4, "tags": ["进阶"], "estimated_hours": 12},
            {"id": "ml_eval", "name": "模型评估与调优", "description": "交叉验证、过拟合、超参数调优", "node_type": "concept", "difficulty": 3, "tags": ["核心"], "estimated_hours": 5},
            {"id": "ml_proj", "name": "实战项目", "description": "完整机器学习项目流程", "node_type": "skill", "difficulty": 3, "tags": ["实践"], "estimated_hours": 10},
        ],
        "edges": [
            {"source_id": "ml_intro", "target_id": "ml_math", "relation_type": "prerequisite", "weight": 1.0, "description": ""},
            {"source_id": "ml_math", "target_id": "ml_supervised", "relation_type": "prerequisite", "weight": 1.0, "description": ""},
            {"source_id": "ml_supervised", "target_id": "ml_unsupervised", "relation_type": "prerequisite", "weight": 0.8, "description": ""},
            {"source_id": "ml_supervised", "target_id": "ml_eval", "relation_type": "prerequisite", "weight": 0.7, "description": ""},
            {"source_id": "ml_unsupervised", "target_id": "ml_deep", "relation_type": "prerequisite", "weight": 0.8, "description": ""},
            {"source_id": "ml_eval", "target_id": "ml_proj", "relation_type": "prerequisite", "weight": 0.9, "description": ""},
            {"source_id": "ml_deep", "target_id": "ml_proj", "relation_type": "prerequisite", "weight": 0.6, "description": ""},
        ],
        "milestones": [
            {"order": 1, "name": "机器学习入门", "description": "了解机器学习的定义、分类和典型应用场景，建立整体认知。", "estimated_hours": 3, "difficulty": "beginner", "topics": ["机器学习定义", "监督vs无监督", "典型应用"], "objectives": ["理解机器学习的基本概念", "能区分监督和无监督学习"], "recommended_resource_types": ["article", "study_guide"]},
            {"order": 2, "name": "数学基础夯实", "description": "复习线性代数、概率论和微积分中的关键知识点。", "estimated_hours": 8, "difficulty": "intermediate", "topics": ["线性代数", "概率统计", "微积分"], "objectives": ["掌握矩阵运算", "理解概率分布"], "recommended_resource_types": ["article", "exercise"]},
            {"order": 3, "name": "核心算法学习", "description": "系统学习监督学习和无监督学习的主流算法。", "estimated_hours": 16, "difficulty": "intermediate", "topics": ["线性回归", "决策树", "聚类算法"], "objectives": ["能手动实现线性回归", "理解决策树原理"], "recommended_resource_types": ["article", "code_example", "exercise"]},
            {"order": 4, "name": "实践与项目", "description": "完成一个完整的机器学习项目：数据预处理、模型训练、评估、调优。", "estimated_hours": 15, "difficulty": "advanced", "topics": ["数据预处理", "模型训练", "评估调优"], "objectives": ["能独立完成ML项目", "会使用交叉验证调优"], "recommended_resource_types": ["code_example", "study_guide", "quiz"]},
        ],
        "total_hours": 42,
        "overview": "机器学习是人工智能的核心领域。本路径从基础概念出发，逐步深入到主流算法和实战项目，帮助你系统掌握机器学习。",
        "tips": ["数学是基础，但不要被公式吓到——先理解直觉再深入数学", "多跑代码实践，Scikit-learn是你最好的伙伴", "参加Kaggle竞赛锻炼实战能力"],
        "materials": ["《机器学习》(周志华)", "Scikit-learn官方文档", "Kaggle竞赛平台"],
        "articles": ["# 机器学习入门\n\n机器学习是人工智能的一个分支，它使计算机能够从数据中学习和改进，而无需明确编程。\n\n## 机器学习分类\n- **监督学习**：使用标注数据训练模型\n- **无监督学习**：从无标注数据中发现模式\n- **强化学习**：通过与环境交互学习\n\n## 学习路线\n1. 掌握Python和数学基础\n2. 学习Scikit-learn库\n3. 从简单算法开始：线性回归、KNN\n4. 逐步深入：决策树、SVM、神经网络", """# 监督学习算法

## 线性回归
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X, y)

## 决策树
通过树形结构做决策，可解释性强。

## 评估指标
准确率、精确率、召回率、F1分数
""", """# 无监督学习

## K-Means聚类
将数据分成K个簇，每个样本属于最近的簇中心。

## PCA降维
主成分分析将高维数据映射到低维空间。

## DBSCAN
基于密度的聚类算法。
""", """# 模型评估与调优

## 交叉验证
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5)

## 过拟合与欠拟合
过拟合：训练集好但泛化差
欠拟合：未能充分学习
""", """# 实战项目流程
1. 问题定义
2. 数据预处理
3. 特征工程
4. 模型训练
5. 评估调优
6. 模型部署
"""],
    },
    "人工智能": {
        "name": "人工智能导论",
        "nodes": [
            {"id": "ai_intro", "name": "人工智能概述", "description": "AI的定义、发展历史、主要流派", "node_type": "topic", "difficulty": 1, "tags": ["入门"], "estimated_hours": 2},
            {"id": "ai_search", "name": "搜索与推理", "description": "状态空间搜索、启发式搜索、逻辑推理", "node_type": "topic", "difficulty": 2, "tags": ["核心"], "estimated_hours": 6},
            {"id": "ai_knowledge", "name": "知识表示", "description": "谓词逻辑、语义网络、框架表示", "node_type": "concept", "difficulty": 2, "tags": ["核心"], "estimated_hours": 4},
            {"id": "ai_ml", "name": "机器学习基础", "description": "监督学习、无监督学习、强化学习概览", "node_type": "topic", "difficulty": 2, "tags": ["核心"], "estimated_hours": 8},
            {"id": "ai_nlp", "name": "自然语言处理", "description": "词向量、RNN、Transformer、大语言模型", "node_type": "topic", "difficulty": 3, "tags": ["进阶"], "estimated_hours": 8},
            {"id": "ai_cv", "name": "计算机视觉", "description": "图像处理基础、CNN、目标检测", "node_type": "topic", "difficulty": 3, "tags": ["进阶"], "estimated_hours": 8},
            {"id": "ai_ethics", "name": "AI伦理与安全", "description": "AI伦理问题、可解释性、公平性", "node_type": "concept", "difficulty": 2, "tags": ["拓展"], "estimated_hours": 3},
        ],
        "edges": [
            {"source_id": "ai_intro", "target_id": "ai_search", "relation_type": "prerequisite", "weight": 1.0, "description": ""},
            {"source_id": "ai_intro", "target_id": "ai_knowledge", "relation_type": "prerequisite", "weight": 1.0, "description": ""},
            {"source_id": "ai_search", "target_id": "ai_ml", "relation_type": "prerequisite", "weight": 0.6, "description": ""},
            {"source_id": "ai_knowledge", "target_id": "ai_nlp", "relation_type": "prerequisite", "weight": 0.5, "description": ""},
            {"source_id": "ai_ml", "target_id": "ai_nlp", "relation_type": "prerequisite", "weight": 0.9, "description": ""},
            {"source_id": "ai_ml", "target_id": "ai_cv", "relation_type": "prerequisite", "weight": 0.9, "description": ""},
            {"source_id": "ai_ml", "target_id": "ai_ethics", "relation_type": "prerequisite", "weight": 0.3, "description": ""},
        ],
        "milestones": [
            {"order": 1, "name": "AI基础认知", "description": "了解人工智能的总体框架、发展历史和核心研究领域。", "estimated_hours": 2, "difficulty": "beginner", "topics": ["AI定义", "发展历史", "研究领域"], "objectives": ["形成AI知识框架", "了解AI的主要流派"], "recommended_resource_types": ["article", "study_guide"]},
            {"order": 2, "name": "经典AI方法", "description": "学习搜索算法、知识表示和逻辑推理等经典AI方法。", "estimated_hours": 10, "difficulty": "intermediate", "topics": ["搜索算法", "知识表示", "逻辑推理"], "objectives": ["理解搜索算法的原理", "掌握知识表示方法"], "recommended_resource_types": ["article", "exercise"]},
            {"order": 3, "name": "现代AI核心", "description": "系统学习机器学习和深度学习的基础知识。", "estimated_hours": 16, "difficulty": "intermediate", "topics": ["机器学习", "神经网络", "深度学习"], "objectives": ["理解ML核心概念", "了解深度学习原理"], "recommended_resource_types": ["article", "code_example", "quiz"]},
            {"order": 4, "name": "AI前沿与应用", "description": "探索NLP、CV等前沿领域，了解AI伦理与安全。", "estimated_hours": 11, "difficulty": "advanced", "topics": ["NLP", "计算机视觉", "AI伦理"], "objectives": ["了解大语言模型原理", "理解AI伦理挑战"], "recommended_resource_types": ["article", "study_guide"]},
        ],
        "total_hours": 39,
        "overview": "人工智能是当今最具变革性的技术之一。本课程从AI的核心理念出发，覆盖经典AI方法到现代深度学习，帮助你全面了解AI技术体系。",
        "tips": ["先建立整体框架再深入细节", "关注算法背后的直觉而非数学推导", "多阅读AI前沿论文和技术博客"],
        "materials": ["《人工智能:一种现代方法》", "CS229机器学习课程", "Hugging Face社区"],
        "articles": ["# 人工智能导论\n\n人工智能(Artificial Intelligence, AI)是研究和开发能够模拟、延伸和扩展人类智能的理论、方法、技术及应用系统的科学。\n\n## AI的主要分支\n- 机器学习与深度学习\n- 自然语言处理\n- 计算机视觉\n- 机器人学\n- 专家系统\n\n## 学习建议\nAI领域发展迅速，建议保持持续学习的习惯，关注顶级会议论文(NeurIPS、ICML、CVPR等)。", """# 搜索算法

## BFS
逐层扩展，保证找到最短路径。

## DFS
沿路径搜索到底再回溯。

## A*算法
结合g(n)和h(n)的最优路径搜索。
""", """# 知识表示

## 一阶谓词逻辑
用谓词和量词表示知识。

## 产生式系统
IF-THEN规则。

## 语义网络
节点和弧表示概念关系。
""", """# 神经网络

## 感知机
最简单的神经网络单元。

## 多层神经网络
通过隐藏层学习非线性特征，用反向传播训练。
""", """# 大语言模型

## Prompt技巧
明确指令、提供示例、分步骤、设定角色

## 典型应用
文本生成、代码审查、翻译、知识图谱
"""],
    },
}

DEFAULT_TOPIC = "人工智能"

def extract_topic_from_prompt(prompt: str) -> str:
    """从提示文本中提取用户想要学习的主题"""
    prompt_lower = prompt.lower()
    
    # 检测常见关键词
    for keyword in ["python", "机器学习", "人工智能", "ai", "deep learning", "深度学习", "数据科学", "java", "前端", "web", "c++"]:
        if keyword in prompt_lower:
            if keyword == "python":
                return "python"
            if keyword in ("人工智能", "ai"):
                return "人工智能"
            if keyword == "机器学习" or keyword == "deep learning" or keyword == "深度学习":
                return "机器学习"
            return keyword
    
    return DEFAULT_TOPIC

def get_course_data(topic_key: str) -> dict:
    """获取课程数据，找不到返回默认"""
    for key in COURSE_TOPICS:
        if topic_key.lower() in key.lower() or topic_key.lower() in key.lower():
            return COURSE_TOPICS[key]
    return COURSE_TOPICS.get(DEFAULT_TOPIC, COURSE_TOPICS["python"])


def fallback_structured(prompt: str) -> dict:
    """根据提示内容返回对应的示范结构化数据"""
    prompt_lower = prompt.lower()
    topic = extract_topic_from_prompt(prompt)
    course = get_course_data(topic)
    course_name = course["name"]

    # ---- 用户画像提取 ----
    if "提取全面的学生画像" in prompt:
        return {
            "name": "学习者",
            "major": course_name,
            "grade": "大一",
            "existing_knowledge": [f"{course_name}基础"],
            "learning_style": "mixed",
            "cognitive_style": "analytical",
            "preferred_difficulty": "beginner",
            "interests": [course_name, "编程"],
            "error_prone_areas": ["基础概念理解"],
            "learning_pace": "normal",
            "motivation": "career",
            "goals": [{"topic": course_name, "description": f"从零开始学习{course_name}"}],
        }

    # ---- 分析用户意图 ----
    if "分析以下用户消息" in prompt or "提取学习意图" in prompt:
        return {
            "intent": "set_goal",
            "topics": [course_name],
            "difficulty": "beginner",
            "needs_clarification": False,
            "clarification_question": "",
            "reply": f"好的！让我为你规划 {course_name} 学习路径，构建知识体系并生成个性化资源！",
        }

    # ---- 知识图谱 ----
    if "构建知识图谱" in prompt:
        return {
            "nodes": course["nodes"],
            "edges": course["edges"],
            "node_count": len(course["nodes"]),
            "edge_count": len(course["edges"]),
        }

    # ---- 学习路径 ----
    if "学习路径" in prompt or "学习计划" in prompt or "里程碑" in prompt or "build" in prompt:
        return {
            "title": f"{course_name}从入门到精通",
            "overview": course["overview"],
            "estimated_total_hours": course["total_hours"],
            "milestones": course["milestones"],
            "learning_tips": course["tips"],
            "recommended_materials": course["materials"],
        }

    # ---- 资源生成 ----
    if "文章" in prompt or "article" in prompt:
        return {"title": course_name, "type": "article", "content_preview": course["articles"][0]}
    if "练习" in prompt or "exercise" in prompt:
        return {"title": f"{course_name}练习题", "type": "exercise", "content_preview": f"# {course_name}练习题\n\n1. 基础概念题\n2. 应用题\n3. 综合题"}
    if "总结" in prompt or "summary" in prompt:
        return {"title": f"{course_name}核心知识总结", "type": "summary", "content_preview": f"# {course_name}知识总结\n\n## 核心概念\n...\n\n## 重点难点\n..."}
    if "指南" in prompt or "study" in prompt:
        return {"title": f"{course_name}学习指南", "type": "study_guide", "content_preview": f"# {course_name}学习指南\n\n## 学习目标\n- 掌握核心概念\n- 能够实际应用\n\n## 学习方法\n..."}

    # ---- 薄弱分析 ----
    if "weak" in prompt or "薄弱" in prompt:
        return {
            "overall_assessment": f"你在{course_name}的基础概念方面掌握不错，但需要加强实践应用能力。",
            "weak_areas": [{"area": "实践应用", "description": "理论理解较好但实际应用经验不足", "suggested_action": "建议完成更多编程练习和项目"}],
            "strong_areas": ["基础概念"],
            "recommended_focus": "建议通过做项目和练习题来巩固所学知识。",
        }

    # ---- 测验生成 ----
    if "测验" in prompt or "quiz" in prompt:
        return {
            "title": f"{course_name} - 随堂测验",
            "questions": [
                {"question": f"以下哪个是{course_name}的核心概念？", "options": ["选项A", "选项B", "选项C", "选项D"], "correct_index": 0, "explanation": "这是核心概念的正确解释", "difficulty": 1},
                {"question": f"{course_name}中___的原理是什么？", "options": ["原理A", "原理B", "原理C", "原理D"], "correct_index": 1, "explanation": "这是标准原理解释", "difficulty": 2},
                {"question": f"在{course_name}中，以下哪个说法是正确的？", "options": ["说法A", "说法B", "说法C", "说法D"], "correct_index": 2, "explanation": "详细解析...", "difficulty": 2},
            ],
        }

    # ---- 智能辅导问答 ----
    if "answer_question" in prompt or "tutor" in prompt_lower:
        q = prompt.split("学生问题：")[-1].split("\n")[0].strip() if "学生问题：" in prompt else ""
        return {
            "summary": f"关于{course_name}中「{q}」的详细解答",
            "detailed_explanation": f"## {q}\n\n这是关于{course_name}中的一个重要知识点。\n\n### 核心概念\n...\n\n### 详细解释\n从基础原理出发，逐步深入理解这个概念。\n\n### 实际应用\n在实际项目中，这个概念被广泛应用在...",
            "code_example": "",
            "visual_description": "",
            "common_misconceptions": [f"常见误区1：关于{q}的错误理解", "常见误区2：混淆相关概念"],
            "follow_up_questions": [f"你能用自己的话解释一下{q}吗？", f"你能举一个{q}的实际应用例子吗？"],
            "related_topics": [f"{course_name}的核心概念", "进阶学习方向"],
        }

    # ---- 学习进度报告 ----
    if "progress_report" in prompt or "学习报告" in prompt:
        return {
            "overall_status": "良好",
            "summary": f"你在{course_name}的学习中表现出色，基础知识掌握扎实，建议继续推进到进阶内容。",
            "mastery_by_topic": {f"{course_name}基础": 75, "核心概念": 60, "实践应用": 40},
            "strengths": [f"{course_name}基础概念理解透彻", "学习态度积极"],
            "weaknesses": ["实践项目经验不足", "综合应用能力有待提高"],
            "recommendations": [
                {"action": "增加编程练习频率", "reason": "有助于巩固理论知识的实际应用", "priority": "高"},
                {"action": "完成一个小型项目", "reason": "项目驱动学习效果最佳", "priority": "中"},
                {"action": "参加在线编程竞赛", "reason": "在实战中提升解决问题的能力", "priority": "低"},
            ],
            "next_milestone": f"完成{course_name}入门阶段的全部学习内容",
            "suggested_difficulty_adjustment": "keep",
        }

    # 默认
    return {"reply": f"好的，让我为你规划{course_name}学习路径！"}


def fallback_text(prompt: str) -> str:
    """根据提示返回示范文本内容"""
    prompt_lower = prompt.lower()
    topic = extract_topic_from_prompt(prompt)
    course = get_course_data(topic)
    course_name = course["name"]

    if "article" in prompt_lower or "\u6587\u7ae0" in prompt_lower:
        return course["articles"][0]
    elif "exercise" in prompt_lower or "练习" in prompt_lower:
        return f"""# {course_name}练习题

## 基础题
1. 简述{course_name}的核心概念。
2. 列举三个{course_name}中的关键技术。
3. 解释以下代码/算法的功能。

## 进阶题
4. 设计一个简单的{course_name}应用场景。
5. 比较两种不同方法的优缺点。
"""
    elif "summary" in prompt_lower or "总结" in prompt_lower:
        return f"""# {course_name}核心知识总结

## 基础概念
- **核心定义**: ...
- **关键技术**: ...
- **应用领域**: ...

## 重点难点
- 理解XXX的原理
- 掌握YYY的方法
- 区分ZZZ和WWW

## 学习路径
从基础到进阶，循序渐进。

## 常用工具
- 工具1
- 工具2
"""
    elif "study" in prompt_lower or "指南" in prompt_lower:
        return f"""# {course_name}学习指南

## 学习目标
- 掌握{course_name}的基础知识
- 能够独立完成相关项目
- 为进一步深入学习打好基础

## 学习方法
1. **理论+实践**: 每学一个概念就动手验证
2. **项目驱动**: 通过完成小项目来巩固
3. **循序渐进**: 从基础到进阶，不要急于求成

## 推荐学习顺序
1. 基础概念
2. 核心技术
3. 实践项目
4. 进阶学习

## 常见问题
- 初学者常见的困惑和解决方法
"""
    elif "code" in prompt_lower or "\u4ee3\u7801" in prompt_lower:
        return f"""# {course_name} \u4ee3\u7801\u793a\u4f8b

## \u793a\u4f8b1\uff1a\u57fa\u7840\u7528\u6cd5
\u2192python
# \u57fa\u7840\u4ee3\u7801\u793a\u4f8b
print("Hello")
class Demo:
    def __init__(self, name):
        self.name = name

## \u793a\u4f8b2\uff1a\u8fdb\u9636\u5e94\u7528
\u2192python
import math
def process(data):
    return [x * 2 for x in data if x > 0]

## \u793a\u4f8b3\uff1a\u5b8c\u6574\u9879\u76ee
\u2192python
def main():
    data = get_input()
    processed = process_data(data)
    save_output(processed)
"""
    else:
        return f"# {course_name}入门\n\n{course_name}是一门非常重要的学科，涵盖广泛的知识体系。\n\n## 核心内容\n- 基础概念\n- 关键技术\n- 实践应用\n\n让我们一起开始{course_name}学习之旅吧！"
