# HR技能训练营

集 **HR技能讲解 · 训练 · 考核** 于一体的 Web 应用（个人学习提升版）。

## 技术栈

- **后端**：Python FastAPI + SQLAlchemy + SQLite（JWT 认证）
- **前端**：Vue 3 + Vite + Vue Router + Pinia + Axios
- **视觉风格**：Constructivism 构成主义设计系统（苏维埃红 `#cc0000` / 纯黑 `#1a1a1a` / 泛黄纸色 `#f2e8d5` 严格三色体系 + 金星色点缀；硬边阴影、对角线构图、Block Invasion 按钮交互）

架构设计借鉴了开源项目：[PlayEdu](https://github.com/PlayEdu/PlayEdu)（企业培训系统功能设计）、[yf-exam-lite](https://github.com/yf-team/yf-exam-lite)（培训+考试闭环）、[quizblitz](https://github.com/jabirmayar/quizblitz)（FastAPI 分层结构）。

## 目录结构

```
HR_Trainner/
├── backend/            # FastAPI 后端
│   ├── app/
│   │   ├── main.py     # 应用入口
│   │   ├── config.py   # 配置
│   │   ├── database.py # 数据库会话
│   │   ├── models.py   # 数据模型
│   │   ├── schemas.py  # Pydantic 模式
│   │   ├── routers/    # 路由（auth / content / placement / practice / progress）
│   │   ├── services/   # 业务逻辑（教学任务计算等）
│   │   ├── utils/      # 工具（JWT、密码哈希）
│   │   ├── content_data.py # 教学内容数据（书单五层 + 贯穿案例）
│   │   └── seed.py     # 种子数据（幂等）
│   ├── smoke_test.py   # 全功能冒烟测试（回归验证）
│   └── data/           # SQLite 数据库文件
├── frontend/           # Vue 3 前端
│   └── src/
│       ├── api/        # Axios 客户端
│       ├── router/     # 路由
│       ├── stores/     # Pinia 状态
│       ├── components/ # 组件（MarkdownBody 等）
│       └── views/      # 页面
├── CONTENT_GUIDE.md    # 教学内容构建指南（书单五层 + 章节结构规范）
├── CASE_STUDY.md       # 贯穿案例（莱茵科技 × 林晓）
└── EXAM_DESIGN.md      # S6 考核模块设计提案
```

## 快速启动

### 1. 后端（端口 8000）

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m app.seed          # 初始化数据库 + 管理员账号 admin/admin123
.venv/bin/uvicorn app.main:app --reload --port 8000
```

接口文档：http://127.0.0.1:8000/docs

回归验证（后端运行中执行）：
```bash
cd backend && ../.venv/bin/python smoke_test.py
```

### 2. 前端（端口 5174）

```bash
cd frontend
npm install
npm run dev
```

访问 http://127.0.0.1:5174（开发期 `/api` 请求自动代理到后端 8000 端口）

## 开发进度

- [x] S1 项目骨架（后端 API + 数据库模型 + 前端工程）✅
- [x] S2 莱茵生命×构成主义样式体系 + 摸底测试模型/API + 种子数据（6模块 + 30摸底题 + 招聘模块样板）✅
- [x] S3 入营能力测试前端（引导页/答题页/结果页/教学任务页）✅
- [x] S4 讲解模块（模块详情/章节阅读/Markdown渲染/完成标记）✅
- [x] S5 训练模块（章节练习/即时反馈/答案解析/练习记录）✅
- [x] S6 考核模块（随机抽题组卷/自动评分/成绩记录/分数-时间曲线/遗忘曲线复习提醒/通过自动标记章节）✅
- [ ] S7 用户与进度统计
- [ ] S8 其余五大模块内容填充
- [ ] S9 联调、全流程测试、检测优化
