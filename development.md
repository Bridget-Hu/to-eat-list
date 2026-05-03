# Development Guide

## 项目概览

To-Eat-List 是一个前后端分离的校园饮食决策工具，当前已经打通的主流程是：

1. 导入菜品数据
2. 填写推荐条件
3. 生成早餐 / 午餐 / 晚餐推荐
4. 自动写入历史记录
5. 在历史记录页查看历史与筛选结果

## 当前技术栈

### 前端

- Vue 3
- Vite
- Vue Router
- Pinia
- ESLint

### 后端

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## 数据层约定

这是当前项目已经落地的正式约定：

- 正式业务数据：SQLite
- 临时导入数据：JSON
- 测试样例 / 调试数据：JSON

### 正式数据

以下数据应以 SQLite 为准：

- 用户偏好
- 正式菜品数据
- 正式历史记录

数据库文件默认位置：

- `backend/to_eat_list.db`

### JSON 的角色

`backend/data/*.json` 不再作为正式业务存储，而是承担这些角色：

- 示例数据
- 临时导入源
- 测试夹具
- 历史遗留 JSON 向 SQLite 的一次性迁移来源

当前典型文件：

- `backend/data/foods.json`
- `backend/data/daily_records.json`

## 当前目录结构

```text
to-eat-list/
├─ frontend/                  # Vue 3 前端
│  ├─ src/
│  │  ├─ pages/
│  │  │  ├─ Home/
│  │  │  ├─ Upload/
│  │  │  ├─ Recommend/
│  │  │  └─ History/
│  │  ├─ router/
│  │  └─ utils/api.js
├─ backend/
│  ├─ app/
│  │  ├─ api/                 # FastAPI 路由
│  │  ├─ db/                  # SQLAlchemy 会话与建表
│  │  ├─ models/              # 数据库模型
│  │  ├─ schemas/             # Pydantic 模型
│  │  └─ services/            # 推荐、导入、迁移、存储服务
│  ├─ data/                   # JSON 示例 / 导入 / 测试数据
│  ├─ run.py
│  └─ to_eat_list.db
├─ docs/
├─ README.md
├─ development.md
└─ todo.md
```

## 环境要求

### Node.js

- 建议版本：`^20.19.0` 或 `>=22.12.0`

### Python

- 建议版本：Python 3.11 或 3.12

## 本地启动

### 1. 启动后端

```powershell
cd backend
python -m pip install -r requirements.txt
python run.py
```

默认地址：

```text
http://127.0.0.1:8000
```

### 2. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

## 开发配置

前端通过 `VITE_API_BASE` 指向后端。

推荐在 `frontend/.env.local` 中配置：

```env
VITE_API_BASE=http://127.0.0.1:8000
```

## 后端接口

### 健康检查

```http
GET /ping
```

### 菜品接口

```http
GET    /foods
DELETE /foods
POST   /foods/upload
POST   /foods/import-sample
```

说明：

- `GET /foods`：读取 SQLite 中的正式菜品数据
- `DELETE /foods`：清空 SQLite 中的正式菜品数据
- `POST /foods/upload`：上传文件并写入 SQLite
- `POST /foods/import-sample`：把 `backend/data/foods.json` 作为示例 JSON 导入 SQLite

当前上传支持：

- `txt`
- `csv`
- `json`

### 推荐接口

```http
POST /recommend/daily
```

请求示例：

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

返回内容包括：

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
- `meals`

### 历史记录接口

```http
GET    /daily-records
DELETE /daily-records
```

说明：

- `GET /daily-records`：读取 SQLite 中的正式历史记录
- `DELETE /daily-records`：清空 SQLite 中的正式历史记录

### 用户偏好接口

```http
POST /user/preferences
GET  /user/preferences/{user_id}
```

## 当前数据流

### 导入菜品

1. 前端上传文件到 `/foods/upload`
2. 后端解析文本或 JSON
3. 把结果写入 SQLite 的 `food_items` 表

### 示例 JSON 导入

1. 调用 `/foods/import-sample`
2. 后端读取 `backend/data/foods.json`
3. 把示例数据写入 SQLite

### 生成推荐

1. 前端调用 `/recommend/daily`
2. 后端从 SQLite 读取正式菜品
3. 计算推荐结果
4. 把历史记录写入 SQLite 的 `daily_records` 表
5. 返回推荐结果给前端

### 历史记录

1. 前端打开 `/history`
2. 调用 `/daily-records`
3. 后端从 SQLite 读取正式历史记录

## 启动时的自动行为

应用启动时会自动执行：

1. 建表
2. 检查是否需要把旧版 JSON 正式数据迁移到 SQLite

这是一次性引导迁移，避免老数据直接丢失。

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

## 现在开发时应遵守的原则

### 1. 正式读写优先走 SQLite

如果是这些内容，就不要再往 JSON 里继续加正式逻辑：

- 菜品正式数据
- 历史记录
- 用户偏好

### 2. JSON 只做导入、样例、测试

如果新增 JSON 文件，应该明确它属于：

- 样例
- 测试
- 临时导入源

而不是新的正式持久化方案。

### 3. 新功能优先补到 service 层

当前推荐逻辑已经拆到 `backend/app/services/recommendation_service.py`，后续功能也应优先按这个方式组织，不要继续把大段业务逻辑堆进路由文件。

## 后续开发建议

优先顺序建议如下：

1. 补核心接口测试
2. 补 `.env.example`
3. 完善菜品管理能力
4. 完善用户偏好前端页面
5. 继续做营养分析、邮件总结、奶茶记录
