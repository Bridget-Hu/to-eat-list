# Development Guide

## 项目概览

To-Eat-List 是一个前后端分离的校园饮食决策工具，当前仓库已经落地的主流程是：

1. 导入菜品数据
2. 填写当天推荐条件
3. 生成一日三餐推荐
4. 自动写入历史记录
5. 在历史记录页查看、筛选、清空历史

当前实现以“可快速本地开发和验证”为主，前端使用 Vue 3 + Vite，后端使用 FastAPI。

## 当前技术栈

### 前端

- Vue 3
- Vite
- Vue Router
- Pinia
- ESLint

### 后端

- FastAPI
- Uvicorn
- Pydantic

### 当前数据存储

虽然 `docs/` 里有 SQLite / SQLAlchemy 的设计草稿，但当前运行中的主要数据存储仍然是本地 JSON 文件：

- `backend/data/foods.json`
- `backend/data/daily_records.json`

也就是说，现阶段项目更接近“文件存储版 MVP”，不是完整数据库版。

## 目录结构

```text
to-eat-list/
├─ frontend/                  # Vue 3 前端
│  ├─ src/
│  │  ├─ pages/               # 页面
│  │  │  ├─ Home/
│  │  │  ├─ Upload/
│  │  │  ├─ Recommend/
│  │  │  └─ History/
│  │  ├─ router/              # 前端路由
│  │  └─ utils/api.js         # fetch 封装与 API_BASE
├─ backend/                   # FastAPI 后端
│  ├─ app/
│  │  ├─ api/                 # 路由
│  │  ├─ services/            # 文件存储与推荐逻辑
│  │  └─ main.py              # FastAPI 入口
│  ├─ data/                   # JSON 数据文件
│  └─ run.py                  # 本地启动脚本
├─ docs/                      # 需求、架构、数据库等设计文档
├─ README.md
└─ development.md             # 当前开发文档
```

## 环境要求

### Node.js

- 建议版本：`^20.19.0` 或 `>=22.12.0`

### Python

- 建议使用 Python 3.11 或 3.12

## 本地启动

### 1. 启动后端

在仓库根目录执行：

```powershell
cd backend
python -m pip install -r requirements.txt
python run.py
```

当前 `backend/run.py` 默认启动地址为：

```text
http://127.0.0.1:8000
```

### 2. 启动前端

在另一个终端执行：

```powershell
cd frontend
npm install
npm run dev
```

默认会启动 Vite 本地开发服务。



## 前端页面说明

当前路由包括：

- `/`：首页
- `/upload`：导入菜品页
- `/recommend`：推荐页
- `/history`：历史记录页

### 首页

作用：

- 展示项目入口
- 引导用户进入导入、推荐、历史记录

### 导入页

作用：

- 上传 `txt / csv / doc / docx`
- 由后端解析后写入 `foods.json`

### 推荐页

作用：

- 提交预算、口味、忌口、突然想吃什么、健康目标、奶茶状态
- 调用推荐接口生成早餐 / 午餐 / 晚餐
- 推荐成功后自动写入历史记录

### 历史记录页

作用：

- 展示累计推荐记录
- 支持关键词搜索
- 支持按目标筛选
- 支持按奶茶状态筛选
- 支持清空历史记录

## 后端接口说明

### 健康检查

```http
GET /ping
```

### 菜品接口

```http
GET    /foods
DELETE /foods
POST   /foods/upload
```

说明：

- `GET /foods`：查看当前已导入菜品
- `DELETE /foods`：清空菜品数据
- `POST /foods/upload`：上传并解析菜品文件

### 推荐接口

```http
POST /recommend/daily
```

请求字段：

```json
{
  "budget": 60,
  "taste": "清淡",
  "dislike": "香菜",
  "want": "牛肉",
  "goal": "减脂",
  "hadMilkTea": false
}
```

返回内容大致包括：

- `breakfast`
- `breakfastReason`
- `lunch`
- `lunchReason`
- `dinner`
- `dinnerReason`
- `summary`
- `totalPrice`
- `remainingBudget`
- `recordId`
- `createdAt`

### 历史记录接口

```http
GET    /daily-records
DELETE /daily-records
```

说明：

- `GET /daily-records`：获取历史记录列表
- `DELETE /daily-records`：清空历史记录

## 当前数据流

### 菜品导入

1. 前端上传文件到 `/foods/upload`
2. 后端解析文本
3. 写入 `backend/data/foods.json`

### 生成推荐

1. 前端提交表单到 `/recommend/daily`
2. 后端读取 `foods.json`
3. 按预算、口味、忌口、目标等规则计算推荐
4. 返回推荐结果
5. 同时把本次结果写入 `backend/data/daily_records.json`

### 历史记录

1. 前端打开 `/history`
2. 调用 `/daily-records`
3. 渲染统计、筛选和记录列表

## 常用开发命令

### 前端

```powershell
cd frontend
npm run dev
npm run lint:eslint
npm run build
```

### 后端

```powershell
cd backend
python run.py
```

## 开发建议

### 1. 优先以“当前代码真实行为”为准

`docs/` 里有不少设计文档，但有一部分还停留在规划阶段。开发时请优先参考：

- `frontend/src/`
- `backend/app/`
- `backend/data/`

而不是直接把 `docs/` 视为已经实现的事实。

### 2. 前后端联调前先确认 API_BASE

这是目前最容易踩坑的一点。若前端报网络错误，先检查：

- 后端是否已启动
- 前端是否指向正确端口

### 3. 当前历史记录不是数据库表

现在历史记录保存在 `daily_records.json`，适合本地调试和快速演示，但不适合多人并发或生产环境。

### 4. 终端显示中文乱码不一定是文件真的坏了

在某些 Windows PowerShell 编码环境下，UTF-8 中文会显示成乱码，但文件本身未必有问题。判断时更应依赖：

- 前端构建是否通过
- ESLint 是否通过
- 后端语法和接口测试是否通过

## 建议的后续迭代

如果继续开发，建议按下面顺序推进：

1. 统一前后端默认端口或补充 `.env.example`
2. 把 JSON 存储迁移到 SQLite / SQLAlchemy
3. 为推荐、上传、历史接口补测试
4. 统一编码和文案，减少中文乱码风险
5. 完善用户信息、邮件、营养分析等尚未真正接通的模块

## 当前状态总结

当前项目已经具备一个完整的 MVP 主流程：

- 可导入菜品
- 可生成推荐
- 可沉淀历史
- 可查看历史

如果后续有人接手开发，这份文档建议和实际代码一起维护，不要只更新 `docs/` 而忘了同步当前运行逻辑。
