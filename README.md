# HR技能训练营

集 **HR技能讲解 · 训练 · 考核** 于一体的应用（个人学习提升版）。

- **Web 版**：FastAPI 后端 + Vue3 前端（含服务端题库/成绩/统计）
- **iOS 单机版**：Capacitor 封装的离线应用（本地数据层替代后端，单用户免登录）

## 技术栈

- **Web 后端**：Python FastAPI + SQLAlchemy + SQLite（JWT 认证）
- **前端**：Vue 3 + Vite + Vue Router + Pinia + Axios
- **iOS 单机版**：Capacitor 8（`frontend/ios/`），内容数据静态打包（`frontend/src/data/app-content.js`），用户数据存 localStorage（`localApi.js`）
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

### 3. iOS 单机版（可选）

```bash
cd frontend
npm install @capacitor/core @capacitor/cli @capacitor/ios
npm run build:ios                    # build + 添加UTF-8 BOM + cap sync（iOS中文修复）
open ios/App/App.xcworkspace       # 在 Xcode 中运行（模拟器或真机）
# 或命令行构建到模拟器：
xcodebuild -project ios/App/App.xcodeproj -scheme App -configuration Debug \
  -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  -derivedDataPath ios/DerivedData build
```

- 单机模式无需后端：内容数据静态打包（`src/data/app-content.js`），学习数据存本机 localStorage，单用户免登录
- 更新内容后重新打包：`cd backend && ../.venv/bin/python export_content.py && cd ../frontend && npm run build:ios`
- 单机模式回归测试：`cd frontend && node test-local.mjs`（34 项）
- **iOS 中文渲染两个必要修复**（已内置在 build:ios 中）：① 构建后为 JS 文件添加 UTF-8 BOM（WKWebView 对无 BOM 外部脚本按非 UTF-8 解码）；② 全局字体栈 `PingFang SC` 前置（`-apple-system` 开头的栈在 WKWebView 中 CJK 回退失败）

## 开发进度

- [x] S1 项目骨架（后端 API + 数据库模型 + 前端工程）✅
- [x] S2 莱茵生命×构成主义样式体系 + 摸底测试模型/API + 种子数据（6模块 + 30摸底题 + 招聘模块样板）✅
- [x] S3 入营能力测试前端（引导页/答题页/结果页/教学任务页）✅
- [x] S4 讲解模块（模块详情/章节阅读/Markdown渲染/完成标记）✅
- [x] S5 训练模块（章节练习/即时反馈/答案解析/练习记录）✅
- [x] S6 考核模块（随机抽题组卷/自动评分/成绩记录/分数-时间曲线/遗忘曲线复习提醒/通过自动标记章节）✅
- [x] S7 用户与进度统计（首页仪表盘/模块考核状态总览/教学任务联动考核状态）✅
- [x] S8 其余五大模块内容填充（劳动法/绩效/薪酬/员工关系/培训，共 15 章案例驱动内容 + 书单五层补强 + 题库扩充至 293 题）✅
- [x] S9 联调、全流程测试、检测优化（端到端闭环测试 16/16 + 冒烟测试 8/8 + 全路由走查）✅

## 功能全景

- **入营摸底测试**：题库随机抽题（每模块 5 题共 30 题）→ 个性化教学任务
- **讲解**：六大模块 20 章案例驱动内容（案例引入→问题→讲解→复盘→费曼自检），Markdown 渲染
- **训练**：每章知识题+案例题，即时反馈与解析，满分自动标记章节完成
- **考核**：随机抽题组卷（7 知识+3 案例）、100 分通过、成绩分数-时间曲线、通过自动标记模块章节
- **学习闭环**：首页仪表盘（进度/摸底/认证/正确率）、遗忘曲线复习提醒、昵称管理

## 测试脚本

```bash
cd backend
../.venv/bin/python smoke_test.py   # 全功能冒烟测试（8 项）
../.venv/bin/python e2e_test.py     # 端到端闭环测试（16 项）
../.venv/bin/python content/validate_modules.py  # 内容 JSON 校验
```
