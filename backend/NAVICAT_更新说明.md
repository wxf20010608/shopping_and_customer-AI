# Navicat 数据库更新说明

## 问题原因

Navicat 为了性能优化会缓存数据库的结构和数据。当数据库结构发生变化时，Navicat 可能不会立即显示更新，需要手动刷新。

## 解决方法

### 方法一：刷新数据库结构（最简单）

1. **刷新表结构**
   - 在 Navicat 左侧连接树中，右键点击数据库连接
   - 选择 `刷新` 或 `Refresh`
   - 或者按快捷键 `F5`

2. **刷新特定表**
   - 展开数据库 → 表
   - 右键点击需要查看的表（如 `orders`）
   - 选择 `刷新表` 或 `Refresh Table`
   - 或者按快捷键 `F5`

3. **重新加载表设计**
   - 打开表后，点击工具栏的 `刷新` 按钮
   - 或按快捷键 `F5` / `Ctrl+R`

### 方法二：重新连接数据库

1. **断开并重新连接**
   - 右键点击数据库连接
   - 选择 `关闭连接` / `Close Connection`
   - 等待 2-3 秒
   - 再次右键点击，选择 `打开连接` / `Open Connection`

2. **完全重新连接**
   - 右键点击数据库连接
   - 选择 `关闭连接` / `Close Connection`
   - 在工具栏点击 `断开` / `Disconnect`
   - 点击 `连接` / `Connect` 重新连接

### 方法三：清空 Navicat 缓存

1. **清空缓存（推荐）**
   - 在 Navicat 菜单栏：`工具` → `选项` → `常规`
   - 点击 `清除缓存` / `Clear Cache`
   - 或者直接关闭并重新打开 Navicat

2. **清除连接缓存**
   - 右键点击数据库连接
   - 选择 `属性` / `Properties`
   - 在 `高级` / `Advanced` 选项卡中
   - 取消勾选 `使用缓存`（如果已勾选），应用后重新勾选

### 方法四：使用 SQL 查询验证

直接在 Navicat 的 SQL 编辑器中运行以下查询来验证表结构是否已更新：

```sql
-- 检查 orders 表的所有列
PRAGMA table_info(orders);

-- 检查 orders 表的新字段是否存在
SELECT sql FROM sqlite_master WHERE type='table' AND name='orders';

-- 查看所有表
SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';

-- 查看 orders 表的数据（包括新字段）
SELECT * FROM orders LIMIT 10;
```

## 数据库文件信息

- **数据库文件路径**: `D:\AI_Learning\02_Project\Shopping_app\backend\smart_mall.db`
- **最后修改时间**: 2026-01-11 01:17:39
- **文件大小**: 46.20 MB
- **表数量**: 15 个

## 已更新的表结构

### Orders 表新增字段：
- ✅ `discount_type` - VARCHAR(20)
- ✅ `discount_amount` - FLOAT DEFAULT 0.0
- ✅ `applied_coupon_id` - INTEGER
- ✅ `deleted_by_user` - BOOLEAN DEFAULT 0
- ✅ `deleted_at` - DATETIME

### Memberships 表新增字段：
- ✅ `plan_id` - INTEGER

### Membership_cards 表新增字段：
- ✅ `published` - BOOLEAN DEFAULT 1

### Coupons 表新增字段：
- ✅ `allowed_product_id` - INTEGER

## 重要提示

⚠️ **如果数据库正在被使用**（FastAPI 后端服务正在运行），Navicat 可能无法立即看到更新。建议：

1. **暂停后端服务**（如果可能）
2. **在 Navicat 中刷新连接**
3. **重新启动后端服务**

## 验证数据库更新

运行以下脚本验证数据库是否已正确更新：

```bash
cd backend
python check_db.py
```

该脚本会显示：
- 数据库文件信息
- 所有表的列表和行数
- 关键表的结构
- 新字段是否存在
