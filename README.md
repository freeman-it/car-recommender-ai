# car-recommender-ai

Car Recommender AI 是一个智能购车推荐系统，旨在帮助那些有购车意愿但面对繁杂的汽车市场不知如何选择的消费者，通过调查问卷的方式快速锁定最适合自己的车型。当前汽车市场车型繁多、参数复杂，普通消费者往往难以在众多品牌、型号、价格区间和能源类型中做出决策。本项目通过问卷形式系统性地收集用户需求，结合 AI 推荐算法，为用户生成个性化的购车方案，有效降低购车筛选成本。

## 功能

- 问卷式需求采集：预算、能源类型、用车场景、座位数、品牌偏好、优先级等
- 本地评分推荐算法：基于规则对车型库逐项打分，输出 Top-N 推荐及理由
- 可选 LLM 增强：接入 OpenAI 兼容接口，生成更自然的个性化推荐说明
- RESTful API：`POST /api/recommend` 提交问卷即返回推荐结果
- 内置车型样本数据（`app/data/cars.json`），可随时扩充
- Vue3 + Three.js 前端：首页白色透明粒子汽车（鼠标靠近粒子打散、离开恢复），分步引导式问卷（每步一题 + 过渡特效）

## 项目结构

```
car-recommender-ai/
├── app/
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理（读取 .env）
│   ├── models/
│   │   ├── questionnaire.py    # 问卷数据模型
│   │   └── recommendation.py   # 车型与推荐结果模型
│   ├── services/
│   │   ├── recommender.py      # 核心评分推荐算法
│   │   └── llm.py              # 可选 LLM 增强
│   ├── routers/
│   │   └── recommend.py        # API 路由
│   └── data/
│       └── cars.json           # 车型样本库
├── frontend/                   # Vue3 + Vite 前端（pnpm 管理）
│   ├── src/
│   │   ├── components/
│   │   │   ├── HeroCar.vue         # Three.js 粒子汽车
│   │   │   ├── QuestionnaireSteps.vue  # 分步引导问卷
│   │   │   └── ResultsView.vue     # 推荐结果展示
│   │   ├── api.js
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── pnpm-lock.yaml          # 依赖锁定文件
│   └── vite.config.js          # 开发代理 /api → 8000
├── tests/                      # pytest 单元测试
├── pyproject.toml              # 项目定义与依赖（uv 使用）
├── uv.lock                     # 依赖锁定文件（勿手动编辑）
├── .env.example
└── README.md
```

## 快速开始（使用 uv）

项目使用 [uv](https://docs.astral.sh/uv/) 管理 Python 环境与依赖，并已锁定 `uv.lock` 保证可复现。首次请先安装 uv：`pip install uv` 或见官网。

### 1. 安装依赖并创建虚拟环境

```bash
uv sync
```

该命令会自动创建 `.venv` 并安装全部依赖（含开发依赖）。以后 `uv sync` 即可保持环境与 `pyproject.toml`/`uv.lock` 一致。

### 2. （可选）配置 LLM

```bash
cp .env.example .env   # Windows: copy .env.example .env
```

在 `.env` 中填入 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`。不填则纯本地推荐。

### 3. 启动服务

```bash
uv run uvicorn app.main:app --reload
```

- 打开 http://127.0.0.1:8000 使用问卷前端页面
- 打开 http://127.0.0.1:8000/docs 查看交互式 API 文档

### 4. 启动前端（开发模式）

前端使用 [pnpm](https://pnpm.io/) 管理依赖（首次先 `npm i -g pnpm`）：

```bash
cd frontend
pnpm install      # 安装依赖（首次）
pnpm dev          # 启动 Vite 开发服务器
```

Vite 开发服务器默认 http://localhost:5173，已配置 `/api` 代理到后端 8000，可直接开发调试。

### 5. 前端构建（生产模式）

```bash
cd frontend
pnpm build        # 输出到 frontend/dist
```

构建后重新启动后端，FastAPI 会自动托管 `frontend/dist`（访问 http://127.0.0.1:8000 即生产版前端）。

### 6. 调用推荐接口

```bash
curl -X POST http://127.0.0.1:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"budget_min":10,"budget_max":20,"energy_type":["混动"],"purpose":"家庭用车","seats":5,"priority":"空间"}'
```

### 7. 运行测试

```bash
uv run pytest
```

## 自定义车型库

编辑 `app/data/cars.json`，按现有字段结构追加车型即可，推荐算法会自动生效。

## License

见 [LICENSE](LICENSE)。
