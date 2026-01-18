# 智慧商城 (Smart Shopping App)

一个功能完整的电商购物平台，采用前后端分离架构，提供商品浏览、购物车、订单管理、会员系统、客服聊天等完整的电商功能。

## 项目简介

智慧商城是一个基于 FastAPI 和 Vue 3 开发的现代化电商平台，支持用户注册登录、商品浏览购买、订单管理、会员系统、优惠券、客服聊天等功能。

## 技术栈

### 后端技术

- **框架**: FastAPI 0.121.2
- **数据库**: SQLite (使用 SQLAlchemy ORM)
- **认证**: Passlib (bcrypt 密码加密)
- **文件处理**: Pillow (图片处理), PyMuPDF (PDF 处理), pytesseract (OCR)
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

- ✅ 在线客服聊天
- ✅ 文件上传（图片、PDF、音频等）
- ✅ 消息历史记录

### 管理功能

- ✅ 管理员后台（访问地址：`http://localhost:5173/admin`）
- ✅ 系统统计概览
- ✅ 用户管理（查看、创建、更新、删除）
- ✅ 商品类别管理
- ✅ 商品管理（查看、创建、更新、删除）
- ✅ 订单管理（查看订单详情、更新订单状态）
- ✅ 客服聊天记录管理
- ✅ 优惠券管理
- ✅ 会员管理

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
│   │   │   ├── coupon_models.py
│   │   │   └── chat_models.py
│   │   ├── routers/           # API 路由
│   │   │   ├── users_route.py
│   │   │   ├── products_route.py
│   │   │   ├── cart_route.py
│   │   │   ├── orders_route.py
│   │   │   ├── logistics_route.py
│   │   │   ├── addresses_route.py
│   │   │   ├── memberships_route.py
│   │   │   ├── coupons_route.py
│   │   │   └── customer_service_route.py
│   │   ├── services/          # 业务逻辑层
│   │   ├── repositories/      # 数据访问层
│   │   ├── static/            # 静态文件（上传的图片、文件等）
│   │   ├── database.py        # 数据库配置
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── admin_router.py    # 管理员路由
│   │   └── schemas.py         # Pydantic 数据模式
│   ├── requirements.txt       # Python 依赖
│   └── smart_mall.db         # SQLite 数据库文件
│
└── frontend/                   # 前端代码
    ├── src/
    │   ├── api/               # API 接口封装
    │   ├── components/        # Vue 组件
    │   ├── views/             # 页面视图
    │   │   ├── auth/          # 认证相关页面
    │   │   ├── products/      # 商品相关页面
    │   │   ├── cart/          # 购物车页面
    │   │   ├── orders/        # 订单相关页面
    │   │   ├── profile/       # 个人中心页面
    │   │   ├── wishlist/      # 心愿单页面
    │   │   ├── chat/          # 客服聊天页面
    │   │   └── admin/         # 管理员页面
    │   ├── stores/            # Pinia 状态管理
    │   ├── router/            # 路由配置
    │   ├── App.vue            # 根组件
    │   └── main.js            # 入口文件
    ├── package.json           # Node.js 依赖
    └── vite.config.js         # Vite 配置
```

## 安装与运行

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

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

确保前端 API 配置文件 `frontend/src/api/index.js` 中的后端地址正确：

```javascript
const API_BASE_URL = 'http://localhost:8000'
```

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

### 客服聊天

- 实时客服消息
- 支持文本、图片、PDF、音频等多种文件类型
- 消息历史记录

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
  - 系统统计概览
  - 用户管理（查看、创建、更新、删除用户）
  - 商品类别管理
  - 商品管理（查看、创建、更新、删除商品）
  - 订单管理（查看订单详情、更新订单状态）
  - 客服聊天记录管理
  - 优惠券管理
  - 会员管理

## 开发注意事项

1. **CORS 配置**: 后端已配置 CORS 中间件，允许跨域请求
2. **静态文件**: 上传的文件存储在 `backend/app/static/uploads/` 目录
3. **数据库迁移**: 项目包含自动数据库迁移逻辑，首次运行会自动创建表和字段
4. **环境变量**: 可以通过 `.env` 文件配置环境变量（需实现 `load_env` 函数）
5. **商品图片自动生成**:
   - 商品图片根据商品名称、分类和ID自动生成固定URL
   - 每个商品对应唯一且固定的图片，确保图片与商品名称一致
   - 系统会自动检测并更新旧格式的图片URL
6. **地址选择功能**:
   - 购物车页面支持从地址簿下拉选择收货地址
   - 默认地址会自动标注并优先显示
   - 使用完整的中国行政区划数据（34个省级行政区，包含所有市、区县）
7. **商品列表随机排序**: 商品列表默认随机排序，每次刷新页面顺序不同

## 后续开发建议

- [ ] 添加支付集成（支付宝、微信支付等）
- [ ] 实现商品评价和评分系统
- [ ] 添加商品推荐算法
- [ ] 实现邮件通知功能
- [ ] 添加商品库存预警
- [ ] 实现优惠券自动发放机制
- [ ] 添加数据统计和分析功能
- [ ] 实现 Redis 缓存优化性能
- [ ] 添加单元测试和集成测试
- [ ] 实现 Docker 容器化部署

## 许可证

本项目仅供学习使用。

## 作者

Adalyn作家

---

如有问题或建议，欢迎提出 Issue 或 Pull Request。
