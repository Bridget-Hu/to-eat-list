# To-Eat-List 架构设计

## 1. 总体架构
本项目采用前后端分离、单仓库管理的方式。

- frontend：负责页面展示、用户输入、结果展示
- backend：负责接口、推荐逻辑、邮件发送、数据库读写
- docs：负责项目说明、需求、任务和设计文档

## 2. 技术选型

### 前端
- Vue 3
- Vite
- Vue Router
- Pinia
- Axios
- Naive UI

前端负责：
- 今日输入页面
- 外卖管理页面
- 推荐结果页面
- 历史记录页面

### 后端
- FastAPI

后端负责：
- 提供 REST API
- 处理用户输入
- 管理外卖数据
- 实现推荐逻辑
- 发送邮件总结

### 数据库
- SQLite（第一阶段）

数据库负责：
- 存储用户信息
- 存储外卖信息
- 存储每日记录
- 存储奶茶记录
- 存储邮件发送记录

## 3. 仓库结构

```bash
to-eat-list/
├─ frontend/
├─ backend/
├─ docs/
└─ README.md