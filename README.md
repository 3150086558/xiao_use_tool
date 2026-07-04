# 小肖的自用工具 v2.0

基于 **Python + FastAPI + Vue 3 + PostgreSQL + Redis** 重构的网页版多功能工具箱。

---

## 一、技术栈

### 后端
- **FastAPI** - 现代异步 Web 框架，自动生成 OpenAPI 文档
- **SQLAlchemy 2.0** - ORM
- **Alembic** - 数据库迁移
- **PostgreSQL** - 主数据库
- **Redis** - 缓存、JWT 黑名单、限流
- **JWT (access + refresh)** - 认证
- **bcrypt** - 密码哈希
- **Celery** - 异步任务队列
- **openpyxl** - Excel 导入导出
- **loguru** - 日志
- **pytest** - 单元测试

### 前端
- **Vue 3 + TypeScript** - 组合式 API + 类型安全
- **Vite** - 构建工具
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router 4** - 路由
- **Axios** - HTTP 客户端
- **ECharts 5** - 图表可视化
- **NProgress** - 路由进度条
- **xlsx (SheetJS)** - 前端 Excel 导出

### 部署
- Docker Compose（PostgreSQL + Redis + Backend + Frontend/Nginx）
- Nginx 反向代理 + 静态资源缓存 + 接口限流

---

## 二、功能模块

### 财务管理
- 记账（新增、编辑、删除、清空全部）
- 多条件筛选（月份、类型、关键词）
- 分页查询
- 收入/支出/结余统计卡片
- 分类汇总
- Excel 导入（含模板下载、防重复、错误提示）
- Excel / CSV 导出
- **统计报表（ECharts 可视化）**
  - 月度收支趋势折线图
  - 分类占比饼图
  - 分类 TOP 排行柱状图

### 日常工具
- 待办事项（增删改查、完成切换、优先级）
- 备忘录（增删改查、搜索）
- 数据库查询工具
  - 连接配置管理（加密存储密码）
  - 支持 PostgreSQL / MySQL / SQLite
  - 测试连接
  - 获取表列表
  - 查看表结构
  - 执行查询（仅允许 SELECT 类语句）

### 系统管理（管理员）
- 用户列表（含记账/待办/备忘录数量统计）
- 重置用户密码
- 删除用户（连同所有关联数据）

### 通用功能
- 多用户注册 / 登录 / 退出
- 修改密码
- 动态菜单树
- 响应式布局
- JWT 自动刷新
- 密码强度可视化

---

## 三、项目结构

```
my_project_python/
├── backend/                         # 后端 FastAPI
│   ├── app/
│   │   ├── main.py                  # FastAPI 入口
│   │   ├── config.py                # 配置（pydantic-settings）
│   │   ├── database.py              # SQLAlchemy 引擎/会话
│   │   ├── redis_client.py          # Redis 连接
│   │   ├── deps.py                  # 依赖注入
│   │   ├── security.py              # JWT、bcrypt
│   │   ├── models/                  # SQLAlchemy ORM 模型
│   │   ├── schemas/                 # Pydantic 请求/响应模型
│   │   ├── api/                     # API 路由
│   │   ├── services/                # 业务逻辑层
│   │   └── utils/                   # 工具函数
│   ├── alembic/                     # 数据库迁移
│   ├── scripts/                     # 脚本（数据迁移等）
│   ├── tests/                       # pytest 测试
│   ├── requirements.txt
│   ├── .env.example
│   ├── run_windows.bat
│   └── run_server.sh
├── frontend/                        # 前端 Vue 3
│   ├── src/
│   │   ├── api/                     # axios 封装 + 接口
│   │   ├── router/                  # 路由
│   │   ├── stores/                  # Pinia
│   │   ├── layouts/                 # 布局组件
│   │   ├── views/                   # 页面
│   │   ├── components/              # 通用组件
│   │   ├── types/                   # TS 类型
│   │   ├── utils/                   # 工具函数
│   │   └── assets/styles/           # 全局样式
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── run_windows.bat
├── deploy/                          # 部署配置
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── test_data/                       # 测试数据（旧版保留）
├── data/                            # SQLite 数据（迁移用）
├── backup/                          # 旧版代码归档
├── .gitignore
└── README.md
```

---

## 四、快速开始

### 方式一：Docker Compose 一键启动

```bash
cd deploy
docker-compose up -d
```

访问：`http://localhost`

默认管理员账号：第一个注册的用户自动成为 admin

### 方式二：本地开发

#### 1. 启动 PostgreSQL 和 Redis
```bash
cd deploy
docker-compose up -d postgres redis
```

#### 2. 启动后端
```bash
cd backend
cp .env.example .env  # 按需修改配置

# Windows
run_windows.bat

# Linux/Mac
./run_server.sh
```

后端地址：`http://127.0.0.1:1112`
API 文档：`http://127.0.0.1:1112/docs`

#### 3. 初始化数据库
```bash
cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate
alembic upgrade head
```

#### 4. 迁移旧 SQLite 数据（可选）
```bash
python scripts/migrate_from_sqlite.py ../data/0701_my_project.db
```
> 迁移后所有用户密码重置为 `Mkld@2026`

#### 5. 启动前端
```bash
cd frontend

# Windows
run_windows.bat

# 或手动
npm install
npm run dev
```

前端地址：`http://127.0.0.1:1111`

---

## 五、数据库表（7 张）

| 表名 | 说明 |
|---|---|
| users | 用户表 |
| records | 记账记录表 |
| menus | 菜单表 |
| todos | 待办事项表 |
| notes | 备忘录表 |
| db_connections | 数据库连接配置（密码加密存储） |
| refresh_tokens | JWT 刷新令牌白名单 |

---

## 六、API 接口

所有接口前缀：`/api/v1`

### 认证
| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /auth/register | 注册 |
| POST | /auth/login | 登录 |
| POST | /auth/logout | 退出 |
| POST | /auth/refresh | 刷新 token |
| POST | /auth/change-password | 修改密码 |
| GET | /auth/me | 当前用户信息 |

### 记账
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /records | 分页查询 |
| POST | /records | 新增 |
| PUT | /records/{id} | 修改 |
| DELETE | /records/{id} | 删除 |
| DELETE | /records | 清空全部 |
| GET | /records/summary | 汇总统计 |
| GET | /records/stats | 报表数据（趋势/饼图） |
| GET | /records/import-template | 下载导入模板 |
| POST | /records/import | 导入 Excel |
| GET | /records/export | 导出 Excel/CSV |

### 待办 / 备忘录 / 菜单
| 方法 | 路径 | 说明 |
|---|---|---|
| GET/POST/PUT/DELETE | /todos[/{id}] | 待办事项 |
| GET/POST/PUT/DELETE | /notes[/{id}] | 备忘录 |
| GET | /menus | 菜单树 |

### 用户管理（admin）
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /users | 用户列表 |
| DELETE | /users/{id} | 删除用户 |
| POST | /users/{id}/reset-password | 重置密码 |

### 数据库查询
| 方法 | 路径 | 说明 |
|---|---|---|
| GET/POST/PUT/DELETE | /db-query/connections[/{id}] | 连接配置管理 |
| POST | /db-query/connect | 测试连接 |
| POST | /db-query/tables | 获取表列表 |
| POST | /db-query/schema | 查看表结构 |
| POST | /db-query/query | 执行查询 |

---

## 七、安全性升级

| 项 | v1.0 | v2.0 |
|---|---|---|
| 密码哈希 | SHA256（无 salt） | bcrypt |
| 会话 | 内存字典 | JWT（access+refresh） |
| CSRF | Cookie 无 SameSite | Bearer Token（天然防护） |
| DB 连接密码 | 明文存储 | AES-GCM 加密存储 |
| Redis | 无 | 有（JWT 黑名单） |
| Nginx 限流 | 无 | 有（60r/m） |

---

## 八、运行测试

### 后端测试
```bash
cd backend
source .venv/bin/activate
pytest -v
```

---

## 九、与 v1.x 的变化

- 后端从 Python 标准库 `http.server` 升级为 FastAPI
- 前端从原生 JS 升级为 Vue 3 + TypeScript + Element Plus
- 数据库统一为 PostgreSQL（移除 SQLite/MySQL 多方言适配）
- 新增 Redis 缓存层
- 新增 ECharts 统计图表
- 密码从 SHA256 升级为 bcrypt
- 会话从内存改为 JWT
- db_connections 表密码从明文改为加密存储
- 新增分页功能
- 新增自动刷新 token
- 新增 Nginx 限流与静态资源缓存
- 旧代码已归档到 `backup/` 目录
