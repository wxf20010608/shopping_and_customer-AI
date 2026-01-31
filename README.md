# 智慧商城 (Smart Shopping App)

一个功能完整的电商购物平台，采用前后端分离架构，提供商品浏览、购物车、订单管理、会员系统、客服聊天等完整的电商功能。

## 项目简介

智慧商城是一个基于 FastAPI 和 Vue 3 开发的现代化电商平台，支持用户注册登录、商品浏览购买、订单管理、会员系统、优惠券、客服聊天、商品评价和评分系统、商品库存预警、数据统计和分析功能、单元测试和集成测试、优惠券自动发放机制以及Redis 缓存优化性能等功能。

## 技术栈

### 后端技术

- **框架**: FastAPI 0.121.2
- **数据库**: SQLite (使用 SQLAlchemy ORM)
- **缓存**: Redis (性能优化，缓存商品列表、商品详情、分类等)
- **认证**: Passlib (bcrypt 密码加密)
- **文件处理**: Pillow (图片处理), PyMuPDF (PDF 处理), pytesseract (OCR), PaddleOCR (OCR), pdfplumber (PDF解析), python-docx (Word解析), openpyxl/xlrd (Excel解析)
- **RAG 向量检索**: FAISS (向量数据库), sentence-transformers (文本嵌入), rank-bm25 (关键词检索), jieba (中文分词)
- **定时任务**: APScheduler (优惠券自动发放定时任务)
- **服务器**: Uvicorn

### 前端技术

- **框架**: Vue 3.4.0
- **构建工具**: Vite 5.0
- **路由**: Vue Router 4.3.0
- **状态管理**: Pinia 2.1.7
- **HTTP 客户端**: Axios 1.6.7
- **工具库**: china-division (中国行政区划)

## 功能特性

### 用户功能

- ✅ 用户注册与登录
- ✅ 个人资料管理
- ✅ 地址簿管理（支持完整的中国行政区划，包含34个省级行政区及所有市、区县）
- ✅ 心愿单/收藏功能

### 商品功能

- ✅ 商品列表浏览（支持分类筛选）
- ✅ 商品搜索（名称、分类）
- ✅ 商品详情查看
- ✅ 商品图片展示（根据商品名称和ID自动生成固定图片，确保图片与商品一一对应）
- ✅ 商品列表随机排序（刷新页面时商品顺序随机变化）
- ✅ **商品评价和评分系统**：
  - 用户评价和评分（1-5分）
  - 评价内容（文字、图片）
  - 购买验证（已验证购买标记）
  - 评价统计（平均评分、评分分布）
  - 评价管理（审核、删除）

### 购物功能

- ✅ 购物车管理（添加、删除、修改数量）
- ✅ 订单创建与管理
- ✅ 订单详情查看
- ✅ 订单物流追踪
- ✅ 订单状态管理
- ✅ 收货地址下拉选择（从地址簿中选择，支持默认地址标识）

### 会员系统

- ✅ 会员计划（标准会员、高级会员）
- ✅ 会员卡管理
- ✅ 会员折扣功能

### 优惠券系统

- ✅ 优惠券领取
- ✅ 优惠券使用
- ✅ 订单优惠券应用

### 客服功能

- ✅ 在线客服聊天（集成 RAG 知识库增强）
- ✅ 文件上传（图片、PDF、音频等）
- ✅ 消息历史记录
- ✅ 支持多模型选择（qwen-turbo/plus/max, qwen-vl-plus/max 等）
- ✅ 智能知识库检索（混合检索：向量相似度 + BM25 关键词）

### 管理功能

- ✅ 管理员后台（访问地址：`http://localhost:5173/admin`）
- ✅ **系统统计概览**（订单、用户、商品、评价、优惠券统计）
- ✅ **数据统计和分析**：
  - 仪表板统计（订单、用户、商品、评价、优惠券）
  - 销售统计（按日期统计订单和销售额，支持自定义天数）
  - 商品统计（最畅销商品、按分类统计）
  - 用户统计（注册趋势、活跃用户、月度注册数据）
- ✅ **商品库存预警**：
  - 低库存商品检查（可配置预警阈值，实时更新统计）
  - 预警级别（缺货、高预警、中预警、低预警）
  - 库存统计（总商品数、低库存数、缺货数，随阈值动态更新）
- ✅ 用户管理（查看、创建、更新、删除）
- ✅ 商品类别管理
- ✅ 商品管理（查看、创建、更新、删除）
- ✅ **商品评价管理**（查看、审核、删除评价）
  - 支持按商品ID筛选
  - 支持按状态筛选（待审核、已通过、已拒绝）
  - 分页浏览评价列表
- ✅ 订单管理（查看订单详情、更新订单状态）
- ✅ 客服聊天记录管理
- ✅ 优惠券管理
- ✅ 会员管理
- ✅ **知识库管理**（RAG 知识库文档管理）
  - 文档创建、更新、删除
  - 支持多种格式导入（PDF、Word、Excel、文本、图片 OCR、网页 URL、数据库表）
  - 文档筛选（按分类、状态筛选）
  - 向量索引管理（自动向量化、索引重建）
  - 知识库搜索测试（混合检索：向量 + BM25）

## 项目结构

```
Shopping_app/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── models/            # 数据模型
│   │   │   ├── user_models.py
│   │   │   ├── product_models.py
│   │   │   ├── cart_models.py
│   │   │   ├── order_models.py
│   │   │   ├── address_models.py
│   │   │   ├── membership_models.py
│   │   │   ├── membership_plan_models.py
│   │   │   ├── membership_card_models.py
│   │   │   ├── coupon_models.py
│   │   │   ├── chat_models.py
│   │   │   ├── knowledge_base_models.py
│   │   │   ├── category_models.py
│   │   │   ├── review_models.py
│   │   │   ├── shipping_models.py
│   │   │   └── timestamp_models.py
│   │   ├── routers/           # API 路由
│   │   │   ├── users_route.py
│   │   │   ├── products_route.py
│   │   │   ├── cart_route.py
│   │   │   ├── orders_route.py
│   │   │   ├── logistics_route.py
│   │   │   ├── addresses_route.py
│   │   │   ├── memberships_route.py
│   │   │   ├── coupons_route.py
│   │   │   ├── customer_service_route.py
│   │   │   ├── knowledge_base_route.py
│   │   │   └── reviews_route.py
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── user_service.py
│   │   │   ├── product_service.py
│   │   │   ├── cart_service.py
│   │   │   ├── order_service.py
│   │   │   ├── address_service.py
│   │   │   ├── membership_service.py
│   │   │   ├── coupon_service.py
│   │   │   ├── coupon_auto_issue_service.py
│   │   │   ├── customer_service.py
│   │   │   ├── logistics_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── document_parser.py
│   │   │   ├── text_cleaner.py
│   │   │   ├── review_service.py
│   │   │   ├── statistics_service.py
│   │   │   ├── stock_alert_service.py
│   │   │   ├── cache_service.py
│   │   │   ├── log_service.py
│   │   │   └── logging_config.py
│   │   ├── repositories/      # 数据访问层
│   │   │   ├── user_repository.py
│   │   │   ├── product_repository.py
│   │   │   ├── cart_repository.py
│   │   │   ├── order_repository.py
│   │   │   ├── address_repository.py
│   │   │   └── logistics_repository.py
│   │   ├── static/            # 静态文件（上传的图片、文件等）
│   │   │   └── uploads/       # 上传文件目录
│   │   ├── utils/             # 工具函数目录
│   │   ├── database.py        # 数据库配置
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── admin_router.py    # 管理员路由
│   │   ├── schemas.py         # Pydantic 数据模式
│   │   └── utils.py           # 工具函数
│   ├── logs/                  # 日志文件目录
│   │   ├── app.log            # 应用日志
│   │   └── error.log          # 错误日志
│   ├── tests/                 # 测试文件
│   │   ├── conftest.py        # pytest 配置
│   │   ├── test_products.py   # 商品服务测试
│   │   ├── test_users.py      # 用户服务测试
│   │   └── test_integration.py # 集成测试
│   ├── requirements.txt       # Python 依赖
│   ├── pytest.ini            # pytest 配置
│   ├── smart_mall.db         # SQLite 数据库文件
│   ├── knowledge_base_index.faiss  # FAISS 向量索引文件
│   ├── Dockerfile            # 后端 Docker 镜像配置
│   └── scripts/              # 工具脚本
│       ├── init_db.py
│       ├── check_db.py
│       └── check_rag.py
│
└── frontend/                   # 前端代码
    ├── src/
    │   ├── api/               # API 接口封装
    │   │   └── index.js       # API 方法定义
    │   ├── components/        # Vue 组件
    │   ├── views/             # 页面视图
    │   │   ├── auth/          # 认证相关页面
    │   │   │   ├── LoginView.vue
    │   │   │   └── RegisterView.vue
    │   │   ├── products/      # 商品相关页面
    │   │   │   ├── ProductList.vue
    │   │   │   └── ProductDetail.vue
    │   │   ├── cart/          # 购物车页面
    │   │   │   └── CartView.vue
    │   │   ├── orders/        # 订单相关页面
    │   │   │   ├── OrdersView.vue
    │   │   │   ├── OrderDetail.vue
    │   │   │   └── OrderLogistics.vue
    │   │   ├── profile/       # 个人中心页面
    │   │   │   ├── ProfileView.vue
    │   │   │   ├── ProfileEditView.vue
    │   │   │   ├── AddressBookView.vue
    │   │   │   ├── MembershipView.vue
    │   │   │   ├── MembershipDetailView.vue
    │   │   │   ├── MembershipPurchaseView.vue
    │   │   │   └── MyReviewsView.vue
    │   │   ├── wishlist/      # 心愿单页面
    │   │   │   └── WishlistView.vue
    │   │   ├── chat/          # 客服聊天页面
    │   │   │   └── ChatView.vue
    │   │   └── admin/         # 管理员页面
    │   │       └── AdminDashboard.vue
    │   ├── stores/            # Pinia 状态管理
    │   │   ├── user.js
    │   │   └── wishlist.js
    │   ├── router/            # 路由配置
    │   │   └── index.js
    │   ├── App.vue            # 根组件
    │   ├── main.js            # 入口文件
    │   └── styles.css         # 全局样式
    ├── public/                # 静态资源
    │   └── pcas.json          # 中国行政区划数据
    ├── dist/                  # 构建产物
    ├── package.json           # Node.js 依赖
    ├── vite.config.js         # Vite 配置
    ├── Dockerfile            # 前端 Docker 镜像配置
    └── nginx/                # Nginx 配置
        └── default.conf      # Nginx 反向代理配置
```

## 安装与运行

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn
- Docker / Docker Compose（可选，推荐）

### Docker 部署（推荐）

#### 前置要求

1. **安装 Docker**：

   - Windows: 下载并安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Linux: 使用包管理器安装 Docker 和 Docker Compose
   - Mac: 下载并安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. **验证 Docker 安装**：

   ```bash
   # 检查 Docker 版本
   docker --version

   # 检查 Docker Compose 版本
   docker compose version
   ```

#### 部署步骤

**第一步：准备环境变量（可选）**

如需配置管理员账户或 AI API Key，可在 `backend/.env` 文件中设置：

```bash
# backend/.env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password
MODEL_API_KEY=your_dashscope_api_key
```

**第二步：构建并启动容器**

在项目根目录（包含 `docker-compose.yml` 的目录）执行：

```bash
# 构建镜像并启动容器（后台运行）
docker compose up -d --build
```

**首次构建可能需要较长时间**（下载依赖、构建镜像等），请耐心等待。

**查看构建日志**：

```bash
# 查看所有服务日志
docker compose logs -f

# 只查看后端日志
docker compose logs -f backend

# 只查看前端日志
docker compose logs -f web
```

**第三步：验证服务**

等待服务启动后（通常需要 1-3 分钟），访问：

- **前端页面**：`http://localhost` 或 `http://127.0.0.1`
- **管理员后台**：`http://localhost/admin`（默认用户名：`admin`，密码：`123456`）
- **后端 API 文档**：`http://localhost/api/docs`（通过 Nginx 代理）

#### 常用操作命令

**查看运行状态**：

```bash
docker compose ps
```

**停止服务**：

```bash
docker compose down
```

**停止并删除数据卷（谨慎操作）**：

```bash
docker compose down -v
```

**重启服务**：

```bash
docker compose restart
```

**重新构建镜像**（代码更新后）：

```bash
docker compose up -d --build
```

**查看容器日志**：

```bash
# 查看所有容器日志
docker compose logs -f

# 查看特定容器日志
docker compose logs -f backend
docker compose logs -f web
```

**进入容器内部**：

```bash
# 进入后端容器
docker compose exec backend bash

# 进入前端容器（nginx）
docker compose exec web sh
```

#### 数据持久化

以下文件/目录会自动映射到宿主机，数据不会丢失：

- **SQLite 数据库**：`./backend/smart_mall.db` → `/app/smart_mall.db`
- **上传文件**：`./backend/app/static/uploads/` → `/app/app/static/uploads/`
- **知识库索引**：`./backend/knowledge_base_index.faiss` → `/app/knowledge_base_index.faiss`

#### 配置说明

**端口映射**：

- 前端（Nginx）：`80:80`（宿主机 80 端口 → 容器 80 端口）
- 后端（FastAPI）：`8000`（仅在容器内部暴露，通过 Nginx 反向代理访问）

**环境变量**（可在 `docker-compose.yml` 中修改）：

```yaml
environment:
  - ADMIN_USERNAME=admin          # 管理员用户名
  - ADMIN_PASSWORD=123456         # 管理员密码
```

**其他环境变量**（AI API Key、RAG 配置等）需要在 `backend/.env` 文件中配置。

#### 故障排查

**问题 1：端口 80 被占用**

```bash
# Windows 查看端口占用
netstat -ano | findstr :80

# Linux/Mac 查看端口占用
lsof -i :80
```

解决方案：修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8080:80"  # 改为 8080 端口
```

**问题 2：容器无法启动**

查看详细日志：

```bash
docker compose logs backend
docker compose logs web
```

**问题 3：Docker 构建失败 - 网络连接问题**

如果构建时出现 `Unable to connect to deb.debian.org` 错误，可能是网络问题：

**解决方案 1：使用国内镜像源（已内置，推荐）**

Dockerfile 已自动配置阿里云镜像源，如果仍然失败，可以手动检查：

```dockerfile
# backend/Dockerfile 中已包含以下配置
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources
```

**解决方案 2：重试构建**

网络问题可能是临时的，可以重试：

```bash
# 清理构建缓存后重试
docker compose build --no-cache backend
```

**解决方案 3：使用代理**

如果有代理，可以在 `docker-compose.yml` 中配置：

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        http_proxy: http://your-proxy:port
        https_proxy: http://your-proxy:port
```

**解决方案 4：手动修改镜像源**

如果自动配置失败，可以手动编辑 Dockerfile：

```dockerfile
# 在 RUN apt-get update 之前添加
RUN echo "deb http://mirrors.aliyun.com/debian/ bookworm main" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian/ bookworm-updates main" >> /etc/apt/sources.list
```

**问题 4：数据库文件权限问题（Linux/Mac）**

确保文件权限正确：

```bash
chmod 644 backend/smart_mall.db
chmod -R 755 backend/app/static/uploads/
```

**问题 5：需要清理所有数据重新开始**

```bash
# 停止并删除容器、网络、数据卷
docker compose down -v

# 删除镜像（可选）
docker rmi smart_mall_backend smart_mall_web
```

### 后端设置

**重要提示**: 所有后端命令都需要在 `backend` 目录下执行！

1. 进入后端目录：

```bash
cd backend
```

2. 创建虚拟环境（推荐）：

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 运行后端服务（**必须在 backend 目录下运行**）：

```bash
# 方式一：从 backend 目录运行（推荐）
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式二：从项目根目录运行（需要设置 PYTHONPATH）
# Windows PowerShell
$env:PYTHONPATH="backend"; uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# Windows CMD
set PYTHONPATH=backend && uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# Linux/Mac
PYTHONPATH=backend uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 `http://localhost:8000` 启动

API 文档可访问：`http://localhost:8000/docs` (Swagger UI)

### 前端设置

1. 进入前端目录：

```bash
cd frontend
```

2. 安装依赖：

```bash
npm install
```

3. 运行开发服务器：

```bash
npm run dev
```

前端应用将在 `http://localhost:5173` 启动（Vite 默认端口）

**主要页面路由**：

- 首页（商品列表）：`http://localhost:5173/`
- 购物车：`http://localhost:5173/cart`
- 订单管理：`http://localhost:5173/orders`
- 个人中心：`http://localhost:5173/profile`
- 心愿单：`http://localhost:5173/wishlist`
- 客服聊天：`http://localhost:5173/chat`
- **管理员后台**：`http://localhost:5173/admin`（默认用户名：`admin`，密码：`123456`）

4. 构建生产版本：

```bash
npm run build
```

构建产物将在 `dist/` 目录中

## API 配置

前端使用相对路径调用后端 API。开发环境通过 Vite 代理，生产环境通过 Nginx 反向代理：

```javascript
const http = axios.create({ baseURL: "/api" })
const adminHttp = axios.create({ baseURL: "/adminapi" })
```

开发环境代理配置位于 `frontend/vite.config.js`，生产环境代理配置位于 `frontend/nginx/default.conf`。

## 数据库

项目使用 SQLite 数据库，数据库文件位于 `backend/smart_mall.db`。

### 数据库初始化

**方式一：自动初始化（推荐）**

首次运行后端服务时，应用会自动创建所有必要的数据库表和初始数据（如会员计划）。

**方式二：手动初始化**

如果需要手动更新数据库结构，可以使用数据库初始化脚本：

```bash
# 进入 backend 目录
cd backend

# 运行初始化脚本
python init_db.py
```

该脚本会执行以下操作：

- ✅ 创建所有数据库表（如果不存在）
- ✅ 检查并添加缺失的列
- ✅ 初始化基础数据（如会员计划）
- ✅ 验证数据库结构完整性

**数据库表列表**：

- `users` - 用户表
- `products` - 商品表
- `categories` - 商品分类表
- `carts` - 购物车表
- `cart_items` - 购物车商品项表
- `orders` - 订单表
- `order_items` - 订单商品项表
- `addresses` - 地址表
- `shipping_info` - 物流信息表
- `memberships` - 会员表
- `membership_plans` - 会员计划表
- `membership_cards` - 会员卡表
- `coupons` - 优惠券表
- `user_coupons` - 用户优惠券关联表
- `chat_messages` - 客服聊天消息表
- `knowledge_documents` - 知识库文档表
- `knowledge_chunks` - 知识库文档块表（用于向量化存储）
- `categories` - 商品分类表

### 数据库备份

建议定期备份数据库文件：

```bash
# Windows PowerShell
Copy-Item backend/smart_mall.db backend/smart_mall_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db

# Linux/Mac
cp backend/smart_mall.db backend/smart_mall_backup_$(date +%Y%m%d_%H%M%S).db
```

### Navicat 刷新数据

如果使用 Navicat 查看数据库时发现数据没有更新，请按以下步骤操作：

1. **刷新数据库结构**（最简单）：

   - 在 Navicat 中右键点击数据库连接 → 选择 `刷新` 或按 `F5`
   - 或者右键点击具体表 → 选择 `刷新表`
2. **重新连接数据库**：

   - 右键点击数据库连接 → `关闭连接`
   - 等待几秒后再次 `打开连接`
3. **使用 SQL 验证**：

   ```sql
   -- 检查表结构是否已更新
   PRAGMA table_info(orders);

   -- 查看所有表
   SELECT name FROM sqlite_master WHERE type='table';
   ```
4. **验证数据库状态**：

   ```bash
   cd backend
   python check_db.py
   ```

如果数据库正在被后端服务使用，建议先暂停服务再刷新 Navicat，或使用只读模式打开。

详细说明请参考：`backend/NAVICAT_更新说明.md`

## 主要功能说明

### 用户认证

- 支持用户注册和登录
- 使用 bcrypt 加密存储密码
- JWT Token 认证（如已实现）

### 商品管理

- 商品分类浏览
- 商品搜索（关键词搜索）
- 商品详情展示
- 库存管理

### 购物车

- 添加商品到购物车
- 修改商品数量
- 删除购物车商品
- 购物车商品结算

### 订单系统

- 创建订单
- 查看订单列表
- 订单详情查看
- 订单状态跟踪
- 物流信息查询

### 会员系统

- 标准会员计划（5% 折扣）
- 高级会员计划（10% 折扣）
- 会员卡购买与管理

### 优惠券

- 优惠券领取
- 优惠券在订单中使用
- 支持商品特定优惠券
- **优惠券自动发放**：
  - 新用户注册自动发放（可配置）
  - 首次购买自动发放（可配置）
  - 定时任务支持（每日检查、生日等）
  - 管理员后台配置自动发放规则

### 客服聊天

- 实时客服消息（集成 RAG 知识库增强回复）
- 支持文本、图片、PDF、音频等多种文件类型
- 消息历史记录（支持时间筛选和跳转定位）
- 多模型支持（文本模型：qwen-turbo/plus/max；视觉模型：qwen-vl-plus/max）
- **RAG 知识库增强**：
  - 混合检索（向量相似度 + BM25 关键词）
  - 自动从知识库检索相关内容并注入到 AI 提示词
  - 自然回复（不显示"根据知识库内容"等标注）

### 知识库管理（RAG）

- **文档管理**：创建、查看、更新、删除知识库文档
- **多格式导入**：
  - 文件上传：PDF、Word、Excel、文本文件
  - 图片 OCR：自动提取图片中的文字
  - 网页导入：从 URL 提取网页内容
  - 数据库导入：从数据库表提取数据
- **文档筛选**：
  - 按分类筛选文档
  - 按状态筛选（有效/无效/全部）
- **向量化存储**：使用 FAISS 存储文档向量，支持快速相似度检索
- **混合检索**：
  - 向量检索（语义相似度）
  - BM25 关键词检索（词匹配）
  - 自动融合两种检索结果，提高准确率和召回率
- **索引管理**：支持重建向量索引和 BM25 索引

### 管理员功能

- 管理员后台访问：`http://localhost:5173/admin`
- 使用 Basic 认证方式登录
- 默认管理员凭据：
  - 用户名：`admin`
  - 密码：`123456`
- 可通过环境变量修改管理员凭据：
  ```bash
  # Windows PowerShell
  $env:ADMIN_USERNAME="your_admin_username"
  $env:ADMIN_PASSWORD="your_admin_password"

  # Windows CMD
  set ADMIN_USERNAME=your_admin_username
  set ADMIN_PASSWORD=your_admin_password

  # Linux/Mac
  export ADMIN_USERNAME=your_admin_username
  export ADMIN_PASSWORD=your_admin_password
  ```
- 管理员功能包括：
  - **系统统计概览**（仪表板数据、销售统计、商品统计、用户统计）
  - **商品库存预警**（低库存商品列表、库存统计、可配置预警阈值）
  - **商品评价管理**（查看、筛选、删除评价，支持按商品ID和状态筛选）
  - 用户管理（查看、创建、更新、删除用户）
  - 商品类别管理
  - 商品管理（查看、创建、更新、删除商品）
  - 订单管理（查看订单详情、更新订单状态）
  - 客服聊天记录管理
  - 优惠券管理（包括自动发放规则配置）
  - 会员管理
  - **知识库管理**（文档管理、多格式导入、状态筛选）
  - **缓存管理**（Redis 缓存状态查看、清空缓存）
  - **日志查看**（查看应用日志、错误日志）

## 开发注意事项

1. **CORS 配置**: 后端已配置 CORS 中间件，允许跨域请求
2. **静态文件**: 上传的文件存储在 `backend/app/static/uploads/` 目录
3. **数据库迁移**: 项目包含自动数据库迁移逻辑，首次运行会自动创建表和字段
4. **环境变量**: 可以通过 `.env` 文件配置环境变量（支持多个路径查找：`backend/.env`、`app/.env`、项目根目录 `.env` 等）

### 环境变量配置

可在 `backend/.env` 文件中配置以下环境变量：

#### 管理员认证

```bash
ADMIN_USERNAME=admin          # 管理员用户名（默认：admin）
ADMIN_PASSWORD=123456         # 管理员密码（默认：123456）
```

#### AI 模型配置（客服聊天）

```bash
MODEL_API_KEY=your_api_key                    # 通义千问 API Key（必需）
DASHSCOPE_API_KEY=your_api_key                # DashScope API Key（备用）
MODEL_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1  # API 基础URL
MODEL_NAME=qwen-turbo                         # 默认文本模型
MODEL_NAME_VL=qwen-vl-plus                    # 默认视觉模型
MODEL_NAME_STT=qwen-audio                     # 语音转文字模型
MODEL_TEMPERATURE=0.7                         # 模型温度参数
MODEL_MAX_LENGTH=2048                         # 最大输出长度
```

#### RAG 知识库配置

```bash
RAG_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5    # 嵌入模型（支持中文/英文/多语言）
RAG_CHUNK_SIZE=500                            # 文档分块大小（字符数）
RAG_CHUNK_OVERLAP=50                          # 分块重叠大小
RAG_TOP_K=5                                   # 检索 Top-K 相关文档
RAG_SIMILARITY_THRESHOLD=0.2                  # 相似度阈值（0-1）
RAG_USE_HYBRID_SEARCH=true                    # 是否使用混合检索（向量+BM25）
RAG_HYBRID_WEIGHT_VECTOR=0.7                  # 向量检索权重
RAG_HYBRID_WEIGHT_BM25=0.3                    # BM25检索权重
```

#### PDF 处理配置

```bash
PDF_MAX_PAGES=20                              # PDF 最大处理页数
PDF_MAX_CHARS=20000                           # PDF 最大字符数
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe  # Tesseract OCR 路径（Windows）
```

#### 聊天历史配置

```bash
CHAT_HISTORY_LIMIT_MAX=5000                   # 聊天历史最大消息数
CHAT_GROUP_THRESHOLD_MS=15000                 # 消息分组时间阈值（毫秒）
```

#### Redis 缓存配置

```bash
REDIS_ENABLED=true                            # 是否启用 Redis 缓存（默认：true）
REDIS_HOST=localhost                          # Redis 服务器地址（默认：localhost）
REDIS_PORT=6379                               # Redis 端口（默认：6379）
REDIS_DB=0                                    # Redis 数据库编号（默认：0）
REDIS_PASSWORD=                               # Redis 密码（可选）
```

#### 优惠券自动发放配置

```bash
COUPON_AUTO_ISSUE_ENABLED=true                # 是否启用优惠券自动发放（默认：true）
COUPON_AUTO_ISSUE_NEW_USER_COUPON_ID=         # 新用户注册自动发放的优惠券ID（可选）
COUPON_AUTO_ISSUE_FIRST_ORDER_COUPON_ID=      # 首次购买自动发放的优惠券ID（可选）
```

#### 商品库存预警配置

```bash
STOCK_ALERT_ENABLED=true                      # 是否启用库存预警（默认：true）
STOCK_ALERT_THRESHOLD=10                      # 库存预警阈值（默认：10）
```

5. **商品图片自动生成**:
   - 商品图片根据商品名称、分类和ID自动生成固定URL
   - 每个商品对应唯一且固定的图片，确保图片与商品名称一致
   - 系统会自动检测并更新旧格式的图片URL
6. **地址选择功能**:
   - 购物车页面支持从地址簿下拉选择收货地址
   - 默认地址会自动标注并优先显示
   - 使用完整的中国行政区划数据（34个省级行政区，包含所有市、区县）
7. **商品列表随机排序**: 商品列表默认随机排序，每次刷新页面顺序不同
8. **RAG 知识库增强**:
   - 客服聊天自动集成知识库检索
   - 支持混合检索（向量相似度 + BM25 关键词），提高准确率
   - 文档自动分块、清洗、向量化存储

## 后续开发建议

- [ ] 添加支付集成（支付宝、微信支付等）
- [X] 实现商品评价和评分系统（评价、评分、图片上传、购买验证）
- [ ] 添加商品推荐算法
- [ ] 实现邮件通知功能
- [X] 添加商品库存预警（支持阈值配置和定时检查）
- [X] 实现优惠券自动发放机制（新用户注册、首次购买等）
- [X] 添加数据统计和分析功能（仪表板、销售统计、商品统计、用户统计）
- [X] 实现 Redis 缓存优化性能（商品列表、商品详情、分类等）
- [X] 添加单元测试和集成测试（pytest框架，覆盖商品、用户等服务）
- [X] 实现 Docker 容器化部署（含 Nginx 反向代理）
- [X] 实现商品评价和评分系统（评价、评分、图片上传、购买验证）

## 测试

项目使用 pytest 进行单元测试和集成测试。

### 运行测试

```bash
# 进入后端目录
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_products.py
pytest tests/test_users.py
pytest tests/test_integration.py

# 显示详细输出
pytest -v
```

### 测试结构

```
backend/tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest 配置和公共 fixtures
├── test_products.py         # 商品服务单元测试
├── test_users.py            # 用户服务单元测试
└── test_integration.py      # 集成测试
```

### 测试覆盖

- **单元测试**：商品服务、用户服务等核心业务逻辑
- **集成测试**：API 端点测试、完整业务流程测试

### 测试数据

测试使用内存数据库（SQLite in-memory），每次测试独立运行，不会影响生产数据。

## 许可证

本项目仅供学习使用。

## 作者

Adalyn作家

---

如有问题或建议，欢迎提出 Issue 或 Pull Request。
