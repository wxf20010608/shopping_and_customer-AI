<!-- frontend/src/views/admin/AdminDashboard.vue -->
<template>
  <section class="admin">
    <h2>管理员系统</h2>
    <div class="card">
      <h3>登录</h3>
      <form class="row" @submit.prevent="login">
        <input v-model="form.username" placeholder="管理员用户名" required />
        <input v-model="form.password" type="password" placeholder="管理员密码" required />
        <button class="btn" type="submit">{{ authed ? '已登录' : '登录' }}</button>
        <button class="btn outline" type="button" @click="checkStatus">检测状态</button>
        <button v-if="authed" class="btn danger" type="button" @click="logoutAdmin">退出管理员</button>
      </form>
      <p class="tips">使用 Basic 认证；凭据仅保存于会话。{{ statusText }}</p>
    </div>

    <div class="tabs">
      <button :class="['tab', {active: active==='stats'}]" @click="active='stats'">统计</button>
      <button :class="['tab', {active: active==='stock'}]" @click="active='stock'">库存预警</button>
      <button :class="['tab', {active: active==='reviews'}]" @click="active='reviews'">评价管理</button>
      <button :class="['tab', {active: active==='users'}]" @click="active='users'">用户</button>
      <button :class="['tab', {active: active==='categories'}]" @click="active='categories'">类别</button>
      <button :class="['tab', {active: active==='products'}]" @click="active='products'">商品</button>
      <button :class="['tab', {active: active==='orders'}]" @click="active='orders'">订单</button>
      <button :class="['tab', {active: active==='chats'}]" @click="active='chats'">客服聊天</button>
      <button :class="['tab', {active: active==='coupons'}]" @click="active='coupons'">优惠券</button>
      <button :class="['tab', {active: active==='memberships'}]" @click="active='memberships'">会员</button>
      <button :class="['tab', {active: active==='knowledge'}]" @click="active='knowledge'">知识库</button>
      <button :class="['tab', {active: active==='cache'}]" @click="active='cache'">缓存管理</button>
      <button :class="['tab', {active: active==='logs'}]" @click="active='logs'">日志查看</button>
    </div>

    <div v-if="active==='stats'" class="card">
      <h3>统计概览</h3>
      <div class="grid">
        <div class="kpi"><strong>用户总数：</strong>{{ dashboardStats.total_users || 0 }}</div>
        <div class="kpi"><strong>商品总数：</strong>{{ dashboardStats.total_products || 0 }}</div>
        <div class="kpi"><strong>订单总数：</strong>{{ dashboardStats.total_orders || 0 }}</div>
        <div class="kpi"><strong>总销售额：</strong>￥{{ (dashboardStats.total_sales_amount || 0).toFixed(2) }}</div>
      </div>
      <div class="list">
        <h4>近7天订单量</h4>
        <p>{{ dashboardStats.recent_orders_7_days || 0 }} 单</p>
      </div>
      <div class="list">
        <h4>热门商品（销量前5）</h4>
        <ul>
          <li v-for="p in (dashboardStats.top_5_products || [])" :key="p.name">
            {{ p.name }}：销量 {{ p.quantity_sold }}
          </li>
        </ul>
      </div>
      
      <!-- 详细统计 -->
      <div class="row" style="margin-top: 16px; gap: 12px;">
        <button class="btn outline" @click="loadSalesStatistics">销售统计</button>
        <button class="btn outline" @click="loadProductStatistics">商品统计</button>
        <button class="btn outline" @click="loadUserStatistics">用户统计</button>
      </div>
      
      <!-- 销售统计 -->
      <div v-if="salesStats !== null" class="list" style="margin-top: 16px;">
        <h4>销售统计（近{{ salesDays }}天）</h4>
        <div class="row">
          <input type="number" v-model.number="salesDays" placeholder="天数" style="width: 80px;" min="1" max="365" />
          <button class="btn" @click="loadSalesStatistics">查询</button>
        </div>
        <ul v-if="salesStats && salesStats.data && salesStats.data.length > 0">
          <li v-for="item in salesStats.data" :key="item.date">
            {{ item.date }}：订单数 {{ item.orders }}，销售额 ￥{{ (item.amount || 0).toFixed(2) }}
          </li>
        </ul>
        <p v-else style="color: #6b7280; padding: 16px;">暂无销售数据</p>
      </div>
      
      <!-- 商品统计 -->
      <div v-if="productStats !== null" class="list" style="margin-top: 16px;">
        <h4>商品销售统计</h4>
        <ul v-if="productStats && productStats.top_products && productStats.top_products.length > 0">
          <li v-for="p in productStats.top_products" :key="p.product_id || p.name">
            {{ p.name || `商品ID: ${p.product_id}` }}：销量 {{ p.quantity_sold || 0 }}，销售额 ￥{{ (p.sales_amount || 0).toFixed(2) }}
          </li>
        </ul>
        <p v-else style="color: #6b7280; padding: 16px;">暂无商品销售数据</p>
      </div>
      
      <!-- 用户统计 -->
      <div v-if="userStats !== null" class="list" style="margin-top: 16px;">
        <h4>用户统计</h4>
        <ul v-if="userStats">
          <li v-if="userStats.total_users !== undefined">总用户数：{{ userStats.total_users }}</li>
          <li v-if="userStats.new_users_today !== undefined">今日新增：{{ userStats.new_users_today }}</li>
          <li v-if="userStats.active_users_7_days !== undefined">近7天活跃：{{ userStats.active_users_7_days }}</li>
          <li v-if="userStats.monthly_registrations && userStats.monthly_registrations.length > 0">
            <strong>用户注册趋势（最近6个月）：</strong>
            <ul style="margin-top: 8px; margin-left: 20px;">
              <li v-for="(reg, idx) in userStats.monthly_registrations.slice(0, 6)" :key="idx">
                {{ reg.year }}-{{ String(reg.month).padStart(2, '0') }}：{{ reg.user_count }} 人
              </li>
            </ul>
          </li>
        </ul>
        <p v-else style="color: #6b7280; padding: 16px;">暂无用户统计数据</p>
      </div>
      
      <button class="btn" @click="loadDashboardStats">刷新概览</button>
    </div>

    <div v-if="active==='stock'" class="card">
      <h3>库存预警</h3>
      <div class="row" style="margin-bottom: 16px;">
        <label>预警阈值：</label>
        <input type="number" v-model.number="stockThreshold" style="width: 80px;" min="0" />
        <button class="btn" @click="loadStockAlerts">查询</button>
        <button class="btn" @click="loadStockStatistics">统计</button>
      </div>
      <div v-if="stockStats" class="list">
        <h4>库存统计</h4>
        <ul>
          <li>总商品数：{{ stockStats.total_products || 0 }}</li>
          <li>低库存商品数：{{ stockStats.low_stock_count || 0 }}</li>
          <li>缺货商品数：{{ stockStats.out_of_stock_count || 0 }}</li>
        </ul>
      </div>
      <div class="list">
        <h4>低库存商品列表</h4>
        <ul v-if="stockAlerts.length > 0">
          <li v-for="alert in stockAlerts" :key="alert.product_id || alert.id" style="padding: 8px; border-bottom: 1px solid #eee;">
            <strong>商品ID：</strong>{{ alert.product_id || alert.id }} | 
            <strong>名称：</strong>{{ alert.product_name || alert.name }} | 
            <strong>当前库存：</strong><span :style="{ color: (alert.current_stock || alert.stock || 0) <= 0 ? 'red' : '#f59e0b' }">{{ alert.current_stock || alert.stock || 0 }}</span>
            <span v-if="alert.alert_level" style="margin-left: 8px; padding: 2px 6px; border-radius: 4px; font-size: 12px;" :style="{ 
              background: alert.alert_level === 'critical' ? '#fee2e2' : alert.alert_level === 'high' ? '#fef3c7' : '#dbeafe',
              color: alert.alert_level === 'critical' ? '#991b1b' : alert.alert_level === 'high' ? '#92400e' : '#1e40af'
            }">
              {{ alert.alert_level === 'critical' ? '缺货' : alert.alert_level === 'high' ? '高预警' : alert.alert_level === 'medium' ? '中预警' : '低预警' }}
            </span>
          </li>
        </ul>
        <p v-else style="color: #6b7280; padding: 16px;">暂无低库存商品</p>
      </div>
    </div>

    <div v-if="active==='reviews'" class="card">
      <h3>评价管理</h3>
      <div class="row" style="margin-bottom: 16px;">
        <input 
          v-model.number="reviewFilter.productId" 
          type="number" 
          placeholder="商品ID（可选）" 
          style="width: 120px;" 
          min="1" 
          @input="handleProductIdInput"
        />
        <select v-model="reviewFilter.status" style="width: 120px;">
          <option value="">全部状态</option>
          <option value="pending">待审核</option>
          <option value="approved">已通过</option>
          <option value="rejected">已拒绝</option>
        </select>
        <button class="btn" @click="loadReviews(1)">查询</button>
        <button class="btn" @click="loadReviews(reviewsList.page || 1)">刷新</button>
      </div>
      <div class="list">
        <h4>评价列表（{{ reviewsList.total || 0 }}条）</h4>
        <ul v-if="reviewsList.items && reviewsList.items.length > 0">
          <li v-for="review in reviewsList.items" :key="review.id" style="padding: 12px; border: 1px solid #e5e7eb; border-radius: 8px; margin-bottom: 8px;">
            <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 8px;">
              <span><strong>评价ID：</strong>{{ review.id }}</span>
              <span><strong>商品ID：</strong>{{ review.product_id }}</span>
              <span><strong>用户ID：</strong>{{ review.user_id }}</span>
              <span><strong>评分：</strong>⭐ {{ review.rating }}</span>
              <span><strong>状态：</strong>{{ review.status }}</span>
              <span v-if="review.verified_purchase" style="background: #10b981; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px;">已购买</span>
            </div>
            <div style="margin-bottom: 8px;">
              <strong>评价内容：</strong>{{ review.comment || '无评价内容' }}
            </div>
            <div v-if="review.images_list && review.images_list.length > 0" style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px;">
              <img v-for="(img, idx) in review.images_list" :key="idx" :src="img" :alt="`评价图片${idx+1}`" style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px;" />
            </div>
            <div style="color: #6b7280; font-size: 14px; margin-bottom: 8px;">
              {{ formatDate(review.created_at) }}
            </div>
            <div class="row">
              <button class="btn danger" @click="deleteReview(review)">删除</button>
            </div>
          </li>
        </ul>
        <p v-else style="color: #6b7280; padding: 16px;">暂无评价</p>
        
        <!-- 分页 -->
        <div v-if="reviewsList.total > reviewsList.page_size" class="pagination">
          <button @click="loadReviews(reviewsList.page - 1)" :disabled="reviewsList.page <= 1">上一页</button>
          <span>第 {{ reviewsList.page }} / {{ Math.ceil(reviewsList.total / reviewsList.page_size) }} 页</span>
          <button @click="loadReviews(reviewsList.page + 1)" :disabled="reviewsList.page >= Math.ceil(reviewsList.total / reviewsList.page_size)">下一页</button>
        </div>
      </div>
    </div>

    <div v-if="active==='users'" class="card">
      <h3>用户管理</h3>
      <form class="row" @submit.prevent="createUser">
        <input v-model="createUserForm.username" placeholder="用户名" required />
        <input v-model="createUserForm.email" placeholder="邮箱" required />
        <input v-model="createUserForm.password" type="password" placeholder="密码" required />
        <input v-model="createUserForm.full_name" placeholder="姓名" />
        <input v-model="createUserForm.phone" placeholder="电话" />
        <input v-model="createUserForm.address" placeholder="默认地址" />
        <button class="btn" type="submit">新增用户</button>
      </form>
      <div class="list">
        <h4>用户列表</h4>
        <ul>
          <li class="row row-users header">
            <span>基本信息</span>
            <span>姓名</span>
            <span>电话</span>
            <span>地址</span>
            <span>操作</span>
          </li>
        </ul>
        <ul>
          <li v-for="u in users" :key="u.id" class="row row-users">
            <span>#{{ u.id }} {{ u.username }} {{ u.email }}</span>
            <input v-model="u.full_name" placeholder="姓名" />
            <input v-model="u.phone" placeholder="电话" />
            <input v-model="u.address" placeholder="地址" />
            <button class="btn outline" @click="updateUser(u)">保存</button>
          </li>
        </ul>
        <button class="btn" @click="loadUsers">刷新</button>
      </div>
    </div>

    <div v-if="active==='categories'" class="card">
      <h3>类别管理</h3>
      <form class="row" @submit.prevent="createCategory">
        <input v-model="newCategory" placeholder="新类别名称" required />
        <button class="btn" type="submit">新增类别</button>
      </form>
      <ul>
        <li v-for="c in categories" :key="c.id" class="row">
          <input v-model="c.name" />
          <button class="btn outline" @click="updateCategory(c)">保存</button>
          <button class="btn danger" @click="deleteCategory(c)">删除</button>
        </li>
      </ul>
      <button class="btn" @click="loadCategories">刷新</button>
    </div>

    <div v-if="active==='products'" class="card">
      <h3>商品管理</h3>
      <form class="row" @submit.prevent="createProduct">
        <input v-model.number="productForm.price" type="number" step="0.01" placeholder="价格" required />
        <input v-model.number="productForm.stock" type="number" placeholder="库存" required />
        <input v-model="productForm.name" placeholder="名称" required />
        <input v-model="productForm.category" placeholder="类别" />
        <input v-model="productForm.description" placeholder="描述" />
        <button class="btn" type="submit">新增商品</button>
      </form>
      <div class="row">
        <textarea v-model="bulkText" rows="6" placeholder='批量导入JSON数组，示例：[{"name":"A","price":1,"stock":1}]'></textarea>
        <button class="btn" @click="bulkImport">批量导入</button>
      </div>
      <div class="list">
        <h4>商品列表</h4>
        <div class="row row-nowrap">
          <input v-model="search" placeholder="搜索名称或分类" @keyup.enter="doSearch" />
          <button class="btn" @click="doSearch">搜索</button>
        </div>
        <ul>
          <li class="row row-products header">
            <span>ID</span>
            <span>名称</span>
            <span>价格</span>
            <span>库存</span>
            <span>类别</span>
            <span>图片</span>
            <span>预览</span>
            <span>保存</span>
            <span>删除</span>
          </li>
        </ul>
        <ul>
          <li v-for="p in products" :key="p.id" class="row row-products">
            <span>#{{ p.id }}</span>
            <input v-model="p.name" placeholder="名称" />
            <input v-model.number="p.price" type="number" step="0.01" placeholder="价格" />
            <input v-model.number="p.stock" type="number" placeholder="库存" />
            <input v-model="p.category" placeholder="类别" />
            <input type="file" accept="image/*" @change="onSelectImage(p, $event)" />
            <img v-if="p.image_url" :src="p.image_url" alt="预览" style="width:48px;height:48px;object-fit:cover;border-radius:6px;border:1px solid #eee;" />
            <button class="btn outline" @click="updateProduct(p)">保存</button>
            <button class="btn danger" @click="deleteProduct(p)">删除</button>
          </li>
        </ul>
        <div class="row pager">
          <button class="btn" :disabled="page <= 1" @click="prevPage">上一页</button>
          <span>第 {{ page }} / {{ totalPages }} 页（共 {{ total }} 条）</span>
          <button class="btn" :disabled="page >= totalPages" @click="nextPage">下一页</button>
        </div>
      </div>
    </div>

    <div v-if="active==='orders'" class="card">
      <h3>订单管理</h3>
      <ul>
        <li class="row row-orders header">
          <span>摘要</span>
          <span>下单时间</span>
          <span>订单状态</span>
          <span>保存状态</span>
          <span>物流状态</span>
          <span>运单号</span>
          <span>保存物流</span>
          <span>用户删除</span>
          <span>删除时间</span>
        </li>
      </ul>
      <ul>
        <li v-for="o in orders" :key="o.id" class="row row-orders">
          <span>#{{ o.id }} {{ o.status }} 合计￥{{ o.total_amount.toFixed(2) }}</span>
          <span>{{ formatDate(o.created_at) }}</span>
          <select v-model="o.status">
            <option value="pending">pending</option>
            <option value="paid">paid</option>
            <option value="shipped">shipped</option>
            <option value="completed">completed</option>
            <option value="cancelled">cancelled</option>
          </select>
          <button class="btn outline" @click="updateOrderStatus(o)">保存状态</button>
          <select v-model="o.shipping.status">
            <option value="created">created</option>
            <option value="in_transit">in_transit</option>
            <option value="delivered">delivered</option>
            <option value="returned">returned</option>
          </select>
          <input v-model="o.shipping.tracking_number" placeholder="运单号" />
          <button class="btn" @click="updateLogistics(o)">保存物流</button>
          <span>{{ o.deleted_by_user ? '是' : '否' }}</span>
          <span>{{ o.deleted_at ? formatDate(o.deleted_at) : '-' }}</span>
        </li>
      </ul>
      <button class="btn" @click="loadOrders">刷新</button>
    </div>

    <div v-if="active==='chats'" class="card">
      <h3>客服聊天管理</h3>
      <div class="row row-nowrap">
        <input v-model.number="chatFilter.userId" type="number" placeholder="用户ID（可选）" />
        <input v-model.number="chatFilter.productId" type="number" placeholder="商品ID（可选）" />
        <select v-model="chatFilter.role">
          <option value="">全部角色</option>
          <option value="user">user</option>
          <option value="assistant">assistant</option>
        </select>
        <input v-model="chatFilter.q" placeholder="关键词（可选）" @keyup.enter="loadChats" />
        <input v-model.number="chatFilter.limit" type="number" min="1" max="500" placeholder="条数" />
        <button class="btn" @click="loadChats">查询</button>
        <button class="btn danger" @click="deleteConversation">删除会话</button>
      </div>
      <ul>
        <li class="row row-chats header">
          <span>ID/时间</span>
          <span>用户/商品</span>
          <span>角色</span>
          <span>内容</span>
          <span>删除</span>
        </li>
      </ul>
      <ul>
        <li v-for="m in chats" :key="m.id" class="row row-chats">
          <span>#{{ m.id }} {{ formatDate(m.created_at) }}</span>
          <span>user#{{ m.user_id }} product#{{ m.product_id || '-' }}</span>
          <span>{{ m.role }}</span>
          <span class="mono">{{ m.content }}</span>
          <button class="btn danger" @click="deleteChat(m)">删除</button>
        </li>
      </ul>
      <button class="btn" @click="loadChats">刷新</button>
    </div>

    <div v-if="active==='coupons'" class="card">
      <h3>优惠券</h3>
      <form class="row" @submit.prevent="createCoupon">
        <input v-model="couponForm.code" placeholder="编码" required />
        <select v-model="couponForm.discount_type">
          <option value="amount">立减金额</option>
          <option value="percent">折扣百分比</option>
        </select>
        <input v-model.number="couponForm.discount_value" type="number" step="0.01" placeholder="数值" required />
        <input v-model.number="couponForm.min_spend" type="number" step="0.01" placeholder="最低消费" />
        <input v-model="couponForm.valid_from" type="datetime-local" placeholder="开始时间" />
        <input v-model="couponForm.valid_to" type="datetime-local" placeholder="结束时间" />
        <input v-model.number="couponForm.allowed_product_id" type="number" placeholder="限制商品ID（仅折扣券）" />
        <label>有效
          <input type="checkbox" v-model="couponForm.active" />
        </label>
        <button class="btn" type="submit">新增优惠券</button>
      </form>
      <div class="list">
        <h4>优惠券列表</h4>
        <ul>
          <li class="row row-coupons header">
            <span>ID/编码</span>
            <span>类型</span>
            <span>数值</span>
            <span>最低消费</span>
            <span>开始/结束</span>
            <span>限制商品</span>
            <span>有效</span>
            <span>保存</span>
            <span>删除</span>
        </li>
        </ul>
        <ul>
          <li v-for="c in coupons" :key="c.id" class="row row-coupons">
            <span>#{{ c.id }} {{ c.code }}</span>
            <select v-model="c.discount_type">
              <option value="amount">amount</option>
              <option value="percent">percent</option>
            </select>
            <input v-model.number="c.discount_value" type="number" step="0.01" />
            <input v-model.number="c.min_spend" type="number" step="0.01" />
            <div class="row row-nowrap">
              <input :value="fmtLocal(c.valid_from)" type="datetime-local" @input="c.valid_from = $event.target.value" />
              <input :value="fmtLocal(c.valid_to)" type="datetime-local" @input="c.valid_to = $event.target.value" />
            </div>
            <input v-model.number="c.allowed_product_id" type="number" placeholder="商品ID" />
            <label>有效<input type="checkbox" v-model="c.active" /></label>
            <button class="btn outline" @click="updateCoupon(c)">保存</button>
            <button class="btn danger" @click="deleteCoupon(c)">删除</button>
          </li>
        </ul>
      </div>
      <div class="row">
        <input v-model.number="assignUserId" type="number" placeholder="用户ID" />
        <select v-model.number="assignCouponId">
          <option v-for="c in coupons" :key="c.id" :value="c.id">#{{ c.id }} {{ c.code }}</option>
        </select>
        <input v-model.number="assignCount" type="number" min="1" placeholder="张数" />
        <button class="btn" @click="assignCoupon">发放给用户</button>
        <label style="margin-left:8px">发放给所有用户<input type="checkbox" v-model="assignAllUsers" /></label>
        <button class="btn" @click="assignCouponBulk">一键发放</button>
      </div>
      <button class="btn" @click="loadCoupons">刷新</button>
      
      <!-- 优惠券自动发放规则管理 -->
      <div class="card" style="margin-top: 24px;">
        <h3>优惠券自动发放规则</h3>
        <div class="row" style="margin-bottom: 16px;">
          <button class="btn" @click="loadAutoIssueRules">刷新规则</button>
          <button class="btn outline" @click="showCreateRuleForm = !showCreateRuleForm">新增规则</button>
        </div>
        
        <!-- 自动发放配置 -->
        <div v-if="autoIssueConfig" class="list" style="margin-bottom: 16px;">
          <h4>自动发放配置</h4>
          <div class="row" style="margin-bottom: 8px;">
            <label>状态：</label>
            <span :style="{ color: autoIssueConfig.enabled ? '#10b981' : '#6b7280' }">
              {{ autoIssueConfig.enabled ? '已启用' : '已禁用' }}
            </span>
          </div>
          <div class="row" style="margin-bottom: 8px;">
            <input v-model.number="autoIssueConfigForm.new_user_coupon_id" type="number" placeholder="新用户注册优惠券ID" style="width: 200px;" />
            <input v-model.number="autoIssueConfigForm.first_order_coupon_id" type="number" placeholder="首次购买优惠券ID" style="width: 200px;" />
            <button class="btn outline" @click="saveAutoIssueConfig">保存配置</button>
          </div>
        </div>
        
        <!-- 创建规则表单 -->
        <div v-if="showCreateRuleForm" class="card" style="margin-bottom: 16px; background: #f9fafb;">
          <h4>新增自动发放规则</h4>
          <form class="row" @submit.prevent="createAutoIssueRule">
            <input v-model="autoIssueRuleForm.rule_id" placeholder="规则ID（可选，自动生成）" />
            <select v-model="autoIssueRuleForm.trigger" required>
              <option value="">选择触发器</option>
              <option value="register">新用户注册</option>
              <option value="first_order">首次购买</option>
              <option value="birthday">生日</option>
              <option value="cron">定时任务（Cron）</option>
              <option value="date">指定日期</option>
            </select>
            <input v-model.number="autoIssueRuleForm.coupon_id" type="number" placeholder="优惠券ID" required />
            <input v-model="autoIssueRuleForm.cron" placeholder="Cron表达式（如使用cron触发器）" />
            <label>启用<input type="checkbox" v-model="autoIssueRuleForm.enabled" /></label>
            <button class="btn" type="submit">创建规则</button>
            <button class="btn outline" type="button" @click="showCreateRuleForm = false">取消</button>
          </form>
        </div>
        
        <!-- 规则列表 -->
        <div class="list">
          <h4>自动发放规则列表（{{ Object.keys(autoIssueRules).length || 0 }}条）</h4>
          <ul v-if="Object.keys(autoIssueRules).length > 0">
            <li v-for="(rule, ruleId) in autoIssueRules" :key="ruleId" style="padding: 12px; border: 1px solid #e5e7eb; border-radius: 8px; margin-bottom: 8px;">
              <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 8px;">
                <span><strong>规则ID：</strong>{{ ruleId }}</span>
                <span><strong>触发器：</strong>{{ rule.trigger }}</span>
                <span><strong>优惠券ID：</strong>{{ rule.coupon_id }}</span>
                <span :style="{ color: rule.enabled ? '#10b981' : '#6b7280' }">
                  {{ rule.enabled ? '已启用' : '已禁用' }}
                </span>
              </div>
              <div v-if="rule.cron" style="margin-bottom: 8px;">
                <strong>Cron表达式：</strong>{{ rule.cron }}
              </div>
              <div class="row">
                <button class="btn outline" @click="toggleAutoIssueRule(ruleId, !rule.enabled)">{{ rule.enabled ? '禁用' : '启用' }}</button>
                <button class="btn danger" @click="deleteAutoIssueRule(ruleId)">删除</button>
              </div>
            </li>
          </ul>
          <p v-else style="color: #6b7280; padding: 16px;">暂无自动发放规则</p>
        </div>
      </div>
    </div>

    <div v-if="active==='memberships'" class="card">
      <h3>会员</h3>
      <form class="row" @submit.prevent="createMembership">
        <input v-model.number="createMembershipUserId" type="number" placeholder="用户ID" required />
        <select v-model="createMembershipForm.level">
          <option value="standard">标准</option>
          <option value="plus">中级</option>
          <option value="premium">高级</option>
        </select>
        <select v-model.number="createMembershipForm.plan_id">
          <option :value="null">无计划</option>
          <option v-for="p in membershipPlans" :key="p.id" :value="p.id">{{ p.name }}（{{ (100-p.discount_percent) }}%折扣）</option>
        </select>
        <input v-model="createMembershipForm.extra_info" placeholder="备注（可选）" />
        <button class="btn" type="submit">开通会员</button>
      </form>
      <p class="hint">填写用户ID → 选择等级与计划 → 可填备注 → 点击“开通会员”。</p>
      <div class="list memberships-list">
        <h4>会员列表</h4>
        <ul>
          <li class="row row-memberships header">
            <span>会员ID/用户ID/余额</span>
            <span>等级</span>
            <span>计划</span>
            <span>状态</span>
            <span>备注</span>
            <span>保存</span>
            <span>删除</span>
          </li>
        </ul>
        <ul>
          <li v-for="m in memberships" :key="m.id" class="row row-memberships">
            <span>#{{ m.id }} 用户#{{ m.user_id }} 余额￥{{ m.balance.toFixed(2) }}</span>
            <select v-model="m.level">
              <option value="standard">standard</option>
              <option value="plus">plus</option>
              <option value="premium">premium</option>
            </select>
            <select v-model.number="m.plan_id">
              <option :value="null">无计划</option>
              <option v-for="p in membershipPlans" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
            <select v-model="m.status">
              <option value="active">active</option>
              <option value="inactive">inactive</option>
            </select>
            <input v-model="m.extra_info" placeholder="备注" />
            <button class="btn outline" @click="updateMembership(m)">保存</button>
            <button class="btn danger" @click="deleteMembership(m)">删除</button>
          </li>
        </ul>
      </div>
      <button class="btn" @click="loadMemberships">刷新</button>

      <h3 style="margin-top:12px">会员计划</h3>
      <form class="row" @submit.prevent="createMembershipPlan">
        <select v-model="membershipPlanLevel" @change="onPlanLevelChange">
          <option value="standard">标准</option>
          <option value="plus">中级</option>
          <option value="premium">高级</option>
        </select>
        <input v-model="membershipPlanForm.code" placeholder="计划编码（唯一）" required />
        <input v-model="membershipPlanForm.name" placeholder="计划名称" required />
        <input v-model.number="membershipPlanForm.discount_percent" type="number" step="0.1" placeholder="折扣百分比（10 表示 9折）" />
        <label>有效<input type="checkbox" v-model="membershipPlanForm.active" /></label>
        <button class="btn" type="submit">新增计划</button>
      </form>
      <p class="hint">示例：折扣百分比填写 10 表示 9折；0 表示不打折。</p>
      <ul>
        <li class="row row-plan header">
          <span>计划ID/编码</span>
          <span>名称</span>
          <span>折扣百分比</span>
          <span>映射级别</span>
          <span>是否在售</span>
          <span>跳转</span>
          <span>操作</span>
        </li>
        <li v-for="p in membershipPlans" :key="p.id" class="row row-plan">
          <span>#{{ p.id }} {{ p.code }}</span>
          <input v-model="p.name" />
          <input v-model.number="p.discount_percent" type="number" step="0.1" />
          <span>{{ planLevel(p) }}</span>
          <label>有效<input type="checkbox" v-model="p.active" /></label>
          <span>
            <router-link class="btn outline" :to="{ name: 'membership-detail', params: { id: p.id } }">详情页</router-link>
            <router-link class="btn" :to="{ name: 'membership-purchase', params: { id: p.id } }">购买页</router-link>
          </span>
          <button class="btn outline" @click="updateMembershipPlan(p)">保存</button>
          <button class="btn danger" @click="deleteMembershipPlan(p)">删除</button>
        </li>
      </ul>

      <h3 style="margin-top:12px">会员卡</h3>
      <form class="row" @submit.prevent="createMembershipCard">
        <input v-model="membershipCardForm.card_no" placeholder="卡号（唯一）" required />
        <select v-model.number="membershipCardForm.plan_id" required>
          <option v-for="p in membershipPlans" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <input v-model.number="membershipCardForm.balance" type="number" step="0.01" placeholder="初始余额" />
        <label>发布<input type="checkbox" v-model="membershipCardForm.published" /></label>
        <button class="btn" type="submit" :disabled="creatingCard">新增会员卡</button>
      </form>
      <p class="hint">创建后可在列表中绑定用户ID并调整余额与状态。</p>
      <ul>
        <li class="row row-card header">
          <span>卡ID/卡号/计划/用户</span>
          <span>余额</span>
          <span>发布</span>
          <span>状态</span>
          <span>操作</span>
        </li>
        <li v-for="c in membershipCards" :key="c.id" class="row row-card">
          <span>#{{ c.id }} {{ c.card_no }} plan#{{ c.plan_id }} user#{{ c.user_id || '-' }} 余额￥{{ c.balance.toFixed(2) }}</span>
          <input v-model.number="c.user_id" type="number" placeholder="用户ID" />
          <input v-model.number="c.balance" type="number" step="0.01" />
          <label>发布<input type="checkbox" v-model="c.published" /></label>
          <select v-model="c.status">
            <option value="unassigned">unassigned</option>
            <option value="assigned">assigned</option>
            <option value="inactive">inactive</option>
          </select>
          <button class="btn outline" @click="updateMembershipCard(c)">保存</button>
          <button class="btn danger" @click="deleteMembershipCard(c)">删除</button>
        </li>
      </ul>
    </div>

    <div v-if="active==='knowledge'" class="card">
      <h3>知识库管理</h3>
      
      <!-- 创建文档 -->
      <div class="card" style="margin-bottom: 16px;">
        <h4>创建文档</h4>
        <form class="row" @submit.prevent="createKnowledgeDocument">
          <input v-model="knowledgeForm.title" placeholder="标题" required />
          <textarea v-model="knowledgeForm.content" rows="4" placeholder="内容" required style="flex: 1; min-width: 300px;"></textarea>
          <input v-model="knowledgeForm.category" placeholder="分类（可选）" />
          <input v-model="knowledgeForm.tags" placeholder="标签，逗号分隔（可选）" />
          <button class="btn" type="submit">创建文档</button>
        </form>
      </div>

      <!-- 从数据库导入 -->
      <div class="card" style="margin-bottom: 16px;">
        <h4>从数据库表导入</h4>
        <form class="row" @submit.prevent="importFromDatabase">
          <input v-model="dbImportForm.table_name" placeholder="表名（如：products）" required />
          <input v-model="dbImportForm.title" placeholder="文档标题（可选）" />
          <input v-model="dbImportForm.category" placeholder="分类（可选）" />
          <input v-model.number="dbImportForm.limit" type="number" placeholder="限制条数" style="width: 120px;" />
          <input v-model="dbImportForm.columns" placeholder="列名，逗号分隔（可选，如：name,price）" style="flex: 1;" />
          <button class="btn" type="submit">导入</button>
        </form>
        <p class="hint">示例：表名填写 "products"，系统会提取商品表数据并添加到知识库</p>
      </div>

      <!-- 从URL导入 -->
      <div class="card" style="margin-bottom: 16px;">
        <h4>从网页URL导入</h4>
        <form class="row" @submit.prevent="importFromUrl">
          <input v-model="urlImportForm.url" placeholder="网页URL（如：https://example.com）" required style="flex: 1;" />
          <input v-model="urlImportForm.title" placeholder="文档标题（可选）" />
          <input v-model="urlImportForm.category" placeholder="分类（可选）" />
          <button class="btn" type="submit">导入</button>
        </form>
      </div>

      <!-- 文件上传 -->
      <div class="card" style="margin-bottom: 16px;">
        <h4>上传文件</h4>
        <div class="row">
          <input type="file" @change="onKnowledgeFileSelect" accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.md,.jpg,.jpeg,.png" />
          <input v-model="fileUploadCategory" placeholder="分类（可选）" />
          <button class="btn" @click="uploadKnowledgeFile" :disabled="!selectedFile">上传</button>
        </div>
        <p class="hint">支持格式：PDF、Word、Excel、文本、Markdown、图片（OCR）</p>
      </div>

      <!-- 文档列表 -->
      <div class="list">
        <h4>文档列表</h4>
        <div class="row row-nowrap">
          <input v-model="knowledgeFilter.category" placeholder="按分类筛选" />
          <select v-model="knowledgeFilter.active">
            <option :value="undefined">全部状态</option>
            <option :value="true">有效</option>
            <option :value="false">无效</option>
          </select>
          <button class="btn" @click="loadKnowledgeDocuments">刷新</button>
          <button class="btn outline" @click="rebuildKnowledgeIndex">重建索引</button>
        </div>
        <ul>
          <li class="row row-knowledge header">
            <span>ID/标题</span>
            <span>分类</span>
            <span>来源</span>
            <span>块数</span>
            <span>质量评分</span>
            <span>状态</span>
            <span>操作</span>
          </li>
        </ul>
        <ul>
          <li v-for="doc in knowledgeDocuments" :key="doc.id" class="row row-knowledge">
            <span>#{{ doc.id }} {{ doc.title }}</span>
            <span>{{ doc.category || '-' }}</span>
            <span>{{ doc.source_type }}</span>
            <span>{{ doc.chunk_count }}</span>
            <span>{{ doc.quality_score ? doc.quality_score.toFixed(2) : '-' }}</span>
            <label>有效<input type="checkbox" v-model="doc.active" @change="updateKnowledgeDocument(doc)" /></label>
            <div class="row row-nowrap">
              <button class="btn outline" @click="viewKnowledgeDocument(doc)">查看</button>
              <button class="btn danger" @click="deleteKnowledgeDocument(doc)">删除</button>
            </div>
          </li>
        </ul>
      </div>

      <!-- 搜索测试 -->
      <div class="card" style="margin-top: 16px;">
        <h4>搜索测试</h4>
        <div class="row">
          <input v-model="knowledgeSearchQuery" placeholder="输入查询内容" style="flex: 1;" />
          <input v-model.number="knowledgeSearchTopK" type="number" placeholder="Top-K" style="width: 80px;" />
          <button class="btn" @click="searchKnowledge">搜索</button>
        </div>
        <div v-if="knowledgeSearchResults.length > 0" style="margin-top: 12px;">
          <h5>搜索结果（{{ knowledgeSearchResults.length }} 条）：</h5>
          <ul>
            <li v-for="(chunk, idx) in knowledgeSearchResults" :key="idx" style="margin: 8px 0; padding: 8px; background: #f9fafb; border-radius: 4px;">
              <strong>文档块 #{{ chunk.chunk_index }}</strong> (文档ID: {{ chunk.document_id }})<br/>
              <span style="color: #666;">{{ chunk.content.substring(0, 200) }}{{ chunk.content.length > 200 ? '...' : '' }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 缓存管理 -->
    <div v-if="active==='cache'" class="card">
      <h3>Redis 缓存管理</h3>
      <div class="row" style="margin-bottom: 16px;">
        <button class="btn" @click="loadCacheStatus">刷新状态</button>
        <button class="btn danger" @click="clearAllCache">清空所有缓存</button>
      </div>
      
      <!-- 缓存状态 -->
      <div v-if="cacheStatus" class="list">
        <h4>缓存状态</h4>
        <ul>
          <li><strong>状态：</strong><span :style="{ color: cacheStatus.enabled ? '#10b981' : '#ef4444' }">{{ cacheStatus.enabled ? '已启用' : '已禁用' }}</span></li>
          <li><strong>连接状态：</strong><span :style="{ color: cacheStatus.connected ? '#10b981' : '#ef4444' }">{{ cacheStatus.connected ? '已连接' : '未连接' }}</span></li>
          <li><strong>缓存键数量：</strong>{{ cacheStatus.keys_count || 0 }}</li>
          <li v-if="cacheStatus.memory_used"><strong>内存使用：</strong>{{ cacheStatus.memory_used }}</li>
          <li v-if="cacheStatus.error" style="color: #ef4444;"><strong>错误：</strong>{{ cacheStatus.error }}</li>
        </ul>
      </div>
      
      <!-- 缓存操作 -->
      <div class="list" style="margin-top: 16px;">
        <h4>缓存操作</h4>
        <div class="row">
          <input v-model="cachePattern" placeholder="缓存键模式（如：product:*）" style="flex: 1;" />
          <button class="btn danger" @click="clearCachePattern">删除匹配的缓存</button>
        </div>
        <p class="hint" style="margin-top: 8px;">提示：可以使用通配符 * 来匹配多个缓存键，例如 "product:*" 会删除所有商品相关的缓存。</p>
      </div>
    </div>

    <!-- 日志查看 -->
    <div v-if="active==='logs'" class="card">
      <h3>日志查看</h3>
      <div class="row" style="margin-bottom: 16px;">
        <button class="btn" @click="loadLogFiles">刷新文件列表</button>
        <button class="btn" @click="loadLogStats">刷新统计</button>
      </div>
      
      <!-- 日志统计 -->
      <div v-if="logStats" class="list" style="margin-bottom: 16px;">
        <h4>日志统计</h4>
        <ul>
          <li><strong>日志目录：</strong>{{ logStats.log_dir }}</li>
          <li><strong>文件数量：</strong>{{ logStats.total_files || 0 }}</li>
          <li><strong>总大小：</strong>{{ logStats.total_size_mb || 0 }} MB</li>
        </ul>
      </div>
      
      <!-- 日志文件列表 -->
      <div class="list" style="margin-bottom: 16px;">
        <h4>日志文件列表</h4>
        <ul v-if="logFiles && logFiles.length > 0">
          <li v-for="file in logFiles" :key="file.name" style="padding: 8px; border-bottom: 1px solid #eee;">
            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
              <span><strong>{{ file.name }}</strong></span>
              <span style="color: #6b7280;">{{ (file.size / 1024).toFixed(2) }} KB</span>
              <span style="color: #6b7280; font-size: 12px;">{{ file.modified ? new Date(file.modified).toLocaleString('zh-CN') : '' }}</span>
              <span v-if="file.type === 'error'" style="background: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px;">错误日志</span>
              <button class="btn outline" style="font-size: 12px; padding: 4px 8px;" @click="readLogFile(file.name)">查看</button>
              <button class="btn danger" style="font-size: 12px; padding: 4px 8px;" @click="clearLogFile(file.name)">清空</button>
            </div>
          </li>
        </ul>
        <p v-else style="color: #6b7280; padding: 16px;">暂无日志文件</p>
      </div>
      
      <!-- 日志查看器 -->
      <div v-if="selectedLogFile" class="card" style="background: #f9fafb;">
        <h4>查看日志：{{ selectedLogFile }}</h4>
        <div class="row" style="margin-bottom: 16px;">
          <input v-model.number="logViewLines" type="number" placeholder="行数" style="width: 100px;" min="100" max="10000" />
          <select v-model="logViewLevel" style="width: 120px;">
            <option value="">全部级别</option>
            <option value="DEBUG">DEBUG</option>
            <option value="INFO">INFO</option>
            <option value="WARNING">WARNING</option>
            <option value="ERROR">ERROR</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
          <input v-model="logViewSearch" placeholder="搜索文本" style="flex: 1;" />
          <label style="display: flex; align-items: center; gap: 4px;">
            <input type="checkbox" v-model="logViewReverse" />
            从末尾读取
          </label>
          <button class="btn" @click="readLogFile(selectedLogFile)">刷新</button>
        </div>
        
        <div v-if="logContent" class="list">
          <h5>日志内容（{{ logContent.filtered_lines || logContent.lines?.length || 0 }} / {{ logContent.total_lines || 0 }} 行）</h5>
          <div v-if="logContent.error" style="color: #ef4444; padding: 12px; background: #fee2e2; border-radius: 4px;">
            <strong>错误：</strong>{{ logContent.error }}
          </div>
          <div v-else style="max-height: 600px; overflow-y: auto; background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 12px; line-height: 1.5;">
            <div v-for="(line, idx) in logContent.lines" :key="idx" style="margin-bottom: 2px; word-wrap: break-word;">
              <span v-if="line.includes(' - ERROR - ')" style="color: #f48771;">{{ line }}</span>
              <span v-else-if="line.includes(' - WARNING - ')" style="color: #dcdcaa;">{{ line }}</span>
              <span v-else-if="line.includes(' - INFO - ')" style="color: #4ec9b0;">{{ line }}</span>
              <span v-else-if="line.includes(' - DEBUG - ')" style="color: #9cdcfe;">{{ line }}</span>
              <span v-else>{{ line }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref, onMounted, computed, watch } from 'vue'
import { api } from '@/api'

const authed = ref(false)
const statusText = ref('')
const form = reactive({ username: '', password: '' })
const active = ref('stats')

const stats = reactive({ users_count: 0, products_count: 0, orders_count: 0, orders_by_status: {}, sales_by_day: [], top_categories: [] })

const users = ref([])
const createUserForm = reactive({ username: '', email: '', password: '', full_name: '', phone: '', address: '' })

const categories = ref([])
const newCategory = ref('')

const productForm = reactive({ name: '', description: '', price: 1, stock: 0, category: '' })
const bulkText = ref('')
const products = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const search = ref('')

const orders = ref([])
const chats = ref([])
const chatFilter = reactive({ userId: null, productId: null, role: '', q: '', limit: 100 })
// 优惠券
const coupons = ref([])
const couponForm = reactive({ code: '', discount_type: 'amount', discount_value: 10, min_spend: 0, valid_from: '', valid_to: '', allowed_product_id: null, active: true })
const assignUserId = ref(null)
const assignCouponId = ref(null)
const assignCount = ref(1)
const assignAllUsers = ref(false)
// 会员
const memberships = ref([])
const createMembershipUserId = ref(null)
const createMembershipForm = reactive({ level: 'standard', extra_info: '' })
const membershipPlans = ref([])
const membershipPlanLevel = ref('standard')
const membershipPlanForm = reactive({ code: '', name: '', discount_percent: 10, active: true })
const membershipCards = ref([])
const creatingCard = ref(false)
const membershipCardForm = reactive({ card_no: '', plan_id: null, balance: 0, published: false })
// 知识库
const knowledgeDocuments = ref([])
const knowledgeForm = reactive({ title: '', content: '', category: '', tags: '' })
const knowledgeFilter = reactive({ category: '', active: undefined })
const dbImportForm = reactive({ table_name: '', title: '', category: '', limit: 1000, columns: '' })
const urlImportForm = reactive({ url: '', title: '', category: '' })
const selectedFile = ref(null)
const fileUploadCategory = ref('')
const knowledgeSearchQuery = ref('')
const knowledgeSearchTopK = ref(5)
const knowledgeSearchResults = ref([])
// 统计数据
const dashboardStats = reactive({ total_users: 0, total_products: 0, total_orders: 0, total_sales_amount: 0, recent_orders_7_days: 0, top_5_products: [] })
// 库存预警
const stockAlerts = ref([])
const stockStats = reactive({ total_products: 0, low_stock_count: 0, out_of_stock_count: 0 })
const stockThreshold = ref(10)
// 详细统计
const salesStats = ref(null)
const salesDays = ref(30)
const productStats = ref(null)
const userStats = ref(null)
// 评价管理
const reviewsList = ref({ items: [], total: 0, page: 1, page_size: 20 })
const reviewFilter = reactive({ productId: null, status: '' })

// 缓存管理
const cacheStatus = ref(null)
const cachePattern = ref('')

// 日志查看
const logFiles = ref([])
const logStats = ref(null)
const selectedLogFile = ref(null)
const logContent = ref(null)
const logViewLines = ref(1000)
const logViewLevel = ref('')
const logViewSearch = ref('')
const logViewReverse = ref(true)

// 优惠券自动发放规则
const autoIssueRules = ref({})
const autoIssueConfig = ref(null)
const autoIssueConfigForm = reactive({ new_user_coupon_id: null, first_order_coupon_id: null })
const showCreateRuleForm = ref(false)
const autoIssueRuleForm = reactive({ rule_id: '', trigger: '', coupon_id: null, cron: '', enabled: true })


function formatDate(d){
  if(!d) return '-'
  try { return new Date(d).toLocaleString() } catch { return String(d) || '-' }
}
function fmtLocal(d){
  try {
    if (!d) return ''
    const dt = new Date(d)
    const pad = (n)=> String(n).padStart(2,'0')
    return `${dt.getFullYear()}-${pad(dt.getMonth()+1)}-${pad(dt.getDate())}T${pad(dt.getHours())}:${pad(dt.getMinutes())}`
  } catch { return '' }
}


async function login(){
  const u = (form.username || '').trim()
  const p = (form.password || '').trim()
  if (!u || !p){ alert('请输入管理员用户名和密码'); return }
  
  // 先设置认证头，确保在发送请求前设置完成
  api.setAdminAuth(u, p)
  
  // 等待一下确保认证头已设置
  await new Promise(resolve => setTimeout(resolve, 10))
  
  try {
    const response = await api.adminStatus()
    authed.value = true
    statusText.value = '管理员服务可用'
    active.value = 'stats'
    await loadDashboardStats()
    form.username = ''
    form.password = ''
  } catch (e) {
    authed.value = false
    api.clearAdminAuth()
    if (e?.response?.status === 401) {
      statusText.value = '认证失败，请检查用户名和密码'
      alert('认证失败，请检查用户名和密码是否正确（默认：admin / 123456）')
    } else if (e?.code === 'ECONNABORTED' || e?.message?.includes('timeout')) {
      statusText.value = '请求超时，请检查后端服务是否运行'
      alert('请求超时，请确保后端服务正在运行（http://127.0.0.1:8000）')
    } else {
      statusText.value = '登录失败：' + (e?.response?.data?.detail || e?.message || '未知错误')
      alert(e?.response?.data?.detail || e?.message || '登录失败')
    }
  }
}

function logoutAdmin(){
  api.clearAdminAuth()
  authed.value = false
  form.username = ''
  form.password = ''
}

async function checkStatus(){
  // 检查是否有认证信息（从 sessionStorage 或 headers 中）
  try {
    const hasAuth = sessionStorage.getItem('admin_basic') || api.adminHttp?.defaults?.headers?.common?.Authorization
    if (!hasAuth) {
      authed.value = false
      statusText.value = '请先登录管理员'
      return
    }
  } catch {}
  
  try {
    await api.adminStatus()
    authed.value = true
    statusText.value = '管理员服务可用'
  } catch (e) {
    authed.value = false
    if (e?.response?.status === 401) {
      statusText.value = '认证失败，请重新登录'
      api.clearAdminAuth()
    } else {
      statusText.value = '管理员服务不可用'
    }
  }
}

async function loadStats(){
  const { data } = await api.adminStats()
  Object.assign(stats, data)
}

async function loadDashboardStats(){
  try {
    const { data } = await api.adminGetDashboardStats()
    Object.assign(dashboardStats, data)
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '加载统计数据失败')
  }
}

async function loadStockAlerts(){
  try {
    const { data } = await api.adminGetStockAlerts(stockThreshold.value || 10)
    stockAlerts.value = data.alerts || []
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '加载库存预警失败')
  }
}

async function loadStockStatistics(){
  try {
    console.log('加载库存统计，阈值:', stockThreshold.value || 10)
    const { data } = await api.adminGetStockStatistics(stockThreshold.value || 10)
    console.log('库存统计数据:', data)
    Object.assign(stockStats, data)
  } catch (e) {
    console.error('加载库存统计失败:', e)
    const errorMsg = e?.response?.data?.detail || e?.response?.data?.message || e?.message || '加载库存统计失败'
    alert(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
  }
}

async function loadSalesStatistics(){
  try {
    console.log('加载销售统计，天数:', salesDays.value || 30)
    const { data } = await api.adminGetSalesStatistics(salesDays.value || 30)
    console.log('销售统计数据:', data)
    salesStats.value = data
    if (!data || !data.data || data.data.length === 0) {
      console.warn('销售统计数据为空')
    }
  } catch (e) {
    console.error('加载销售统计失败:', e)
    const errorMsg = e?.response?.data?.detail || e?.response?.data?.message || e?.message || '加载销售统计失败'
    alert(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
  }
}

async function loadProductStatistics(){
  try {
    console.log('加载商品统计')
    const { data } = await api.adminGetProductStatistics()
    console.log('商品统计数据:', data)
    productStats.value = data
    if (!data || !data.top_products || data.top_products.length === 0) {
      console.warn('商品统计数据为空')
    }
  } catch (e) {
    console.error('加载商品统计失败:', e)
    const errorMsg = e?.response?.data?.detail || e?.response?.data?.message || e?.message || '加载商品统计失败'
    alert(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
  }
}

async function loadUserStatistics(){
  try {
    console.log('加载用户统计')
    const { data } = await api.adminGetUserStatistics()
    console.log('用户统计数据:', data)
    userStats.value = data
    if (!data) {
      console.warn('用户统计数据为空')
    }
  } catch (e) {
    console.error('加载用户统计失败:', e)
    const errorMsg = e?.response?.data?.detail || e?.response?.data?.message || e?.message || '加载用户统计失败'
    alert(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
  }
}

// 处理商品ID输入，确保只能是正整数或null
function handleProductIdInput(event) {
  const value = event.target.value
  if (value === '' || value === null || value === undefined) {
    reviewFilter.productId = null
  } else {
    const num = parseInt(value)
    if (isNaN(num) || num < 1) {
      // 如果输入无效或小于1，清空输入框
      reviewFilter.productId = null
      event.target.value = ''
    } else {
      reviewFilter.productId = num
    }
  }
}

async function loadReviews(page = 1){
  try {
    // 确保 page 是数字，防止事件对象被传递
    let actualPage = page
    if (typeof page !== 'number') {
      console.warn('loadReviews 收到非数字参数，使用默认值 1:', page)
      actualPage = reviewsList.value.page || 1
    } else {
      actualPage = Math.max(1, Math.floor(actualPage)) // 确保是正整数
    }
    
    // 重置页码（如果点击查询或刷新）
    if (actualPage === 1) {
      reviewsList.value.page = 1
    }
    
    // 处理筛选参数：只接受大于0的正整数，其他情况转为 undefined
    const productId = (reviewFilter.productId && typeof reviewFilter.productId === 'number' && reviewFilter.productId > 0) ? reviewFilter.productId : undefined
    const status = reviewFilter.status && reviewFilter.status.trim() ? reviewFilter.status.trim() : undefined
    
    console.log('加载评价列表，筛选条件:', { productId, status }, '页码:', actualPage)
    const { data } = await api.adminListReviews(
      productId,
      status,
      actualPage,
      20
    )
    
    // 确保数据结构正确
    if (data && typeof data === 'object') {
      reviewsList.value = {
        items: data.items || [],
        total: data.total || 0,
        page: data.page || actualPage,
        page_size: data.page_size || 20
      }
      
      // 解析图片JSON（后端已处理，但前端也处理以防万一）
      if (reviewsList.value.items) {
        reviewsList.value.items.forEach(item => {
          if (item.images && typeof item.images === 'string') {
            try {
              item.images_list = JSON.parse(item.images)
            } catch {
              item.images_list = []
            }
          } else if (item.images_list) {
            // 后端已解析
            item.images_list = item.images_list
          } else {
            item.images_list = []
          }
        })
      }
    } else {
      console.error('返回数据格式错误:', data)
      alert('返回数据格式错误，请查看控制台')
    }
  } catch (e) {
    console.error('加载评价列表失败:', e)
    const errorMsg = e?.response?.data?.detail || e?.response?.data?.message || e?.message || '加载评价列表失败'
    alert(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
  }
}

async function deleteReview(review){
  if (!review || !review.id) {
    alert('评价信息无效')
    return
  }
  if (!confirm(`确认删除评价 #${review.id}？`)) return
  try {
    await api.adminDeleteReview(review.id)
    // 删除成功后重新加载当前页
    const currentPage = reviewsList.value.page || 1
    await loadReviews(currentPage)
    alert('删除成功')
  } catch (e) {
    console.error('删除评价失败:', e)
    const errorMsg = e?.response?.data?.detail || e?.response?.data?.message || e?.message || '删除失败'
    alert(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
  }
}

// 缓存管理函数
async function loadCacheStatus(){
  try {
    const { data } = await api.adminGetCacheStatus()
    cacheStatus.value = data
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '加载缓存状态失败')
  }
}

async function clearAllCache(){
  if (!confirm('确认清空所有缓存？')) return
  try {
    const { data } = await api.adminClearCache()
    alert(data.message || '缓存已清空')
    await loadCacheStatus()
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '清空缓存失败')
  }
}

async function clearCachePattern(){
  if (!cachePattern.value) {
    alert('请输入缓存键模式')
    return
  }
  if (!confirm(`确认删除匹配 "${cachePattern.value}" 的缓存？`)) return
  try {
    const { data } = await api.adminDeleteCachePattern(cachePattern.value)
    alert(data.message || `已删除 ${data.deleted_count || 0} 个缓存键`)
    cachePattern.value = ''
    await loadCacheStatus()
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '删除缓存失败')
  }
}

// 日志查看函数
async function loadLogFiles(){
  try {
    const { data } = await api.adminListLogFiles()
    logFiles.value = data
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '加载日志文件列表失败')
  }
}

async function loadLogStats(){
  try {
    const { data } = await api.adminGetLogStats()
    logStats.value = data
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '加载日志统计失败')
  }
}

async function readLogFile(filename){
  try {
    selectedLogFile.value = filename
    const { data } = await api.adminReadLogFile(
      filename,
      logViewLines.value || 1000,
      logViewLevel.value || null,
      logViewSearch.value || null,
      logViewReverse.value
    )
    logContent.value = data
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '读取日志文件失败')
  }
}

async function clearLogFile(filename){
  if (!confirm(`确认清空日志文件 "${filename}"？`)) return
  try {
    const { data } = await api.adminClearLogFile(filename)
    alert(data.message || '日志文件已清空')
    await loadLogFiles()
    await loadLogStats()
    if (selectedLogFile.value === filename) {
      await readLogFile(filename)
    }
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '清空日志文件失败')
  }
}

// 优惠券自动发放规则管理函数
async function loadAutoIssueRules(){
  try {
    const { data } = await api.adminGetAutoIssueRules()
    autoIssueRules.value = data.rules || {}
    autoIssueConfig.value = data
    if (data.config) {
      autoIssueConfigForm.new_user_coupon_id = data.config.COUPON_AUTO_ISSUE_NEW_USER_COUPON_ID ? parseInt(data.config.COUPON_AUTO_ISSUE_NEW_USER_COUPON_ID) : null
      autoIssueConfigForm.first_order_coupon_id = data.config.COUPON_AUTO_ISSUE_FIRST_ORDER_COUPON_ID ? parseInt(data.config.COUPON_AUTO_ISSUE_FIRST_ORDER_COUPON_ID) : null
    }
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '加载自动发放规则失败')
  }
}

async function createAutoIssueRule(){
  try {
    const payload = { ...autoIssueRuleForm }
    if (!payload.rule_id) delete payload.rule_id
    if (!payload.cron) delete payload.cron
    const { data } = await api.adminCreateAutoIssueRule(payload)
    alert(data.message || '规则已创建')
    showCreateRuleForm.value = false
    Object.keys(autoIssueRuleForm).forEach(k => {
      if (k === 'enabled') autoIssueRuleForm[k] = true
      else autoIssueRuleForm[k] = ''
    })
    await loadAutoIssueRules()
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '创建规则失败')
  }
}

async function toggleAutoIssueRule(ruleId, enabled){
  try {
    await api.adminUpdateAutoIssueRule(ruleId, { enabled })
    await loadAutoIssueRules()
    alert(enabled ? '规则已启用' : '规则已禁用')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '更新规则失败')
  }
}

async function deleteAutoIssueRule(ruleId){
  if (!confirm(`确认删除规则 "${ruleId}"？`)) return
  try {
    await api.adminDeleteAutoIssueRule(ruleId)
    await loadAutoIssueRules()
    alert('规则已删除')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '删除规则失败')
  }
}

async function saveAutoIssueConfig(){
  try {
    const payload = {}
    if (autoIssueConfigForm.new_user_coupon_id) {
      payload.COUPON_AUTO_ISSUE_NEW_USER_COUPON_ID = autoIssueConfigForm.new_user_coupon_id
    }
    if (autoIssueConfigForm.first_order_coupon_id) {
      payload.COUPON_AUTO_ISSUE_FIRST_ORDER_COUPON_ID = autoIssueConfigForm.first_order_coupon_id
    }
    await api.adminSetAutoIssueConfig(payload)
    alert('配置已保存')
    await loadAutoIssueRules()
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '保存配置失败')
  }
}

async function loadUsers(){
  const { data } = await api.adminListUsers()
  users.value = data
}

async function createUser(){
  const { data } = await api.adminCreateUser(createUserForm)
  users.value.unshift(data)
  Object.keys(createUserForm).forEach(k => createUserForm[k] = '')
}

async function updateUser(u){
  try {
    const payload = { full_name: u.full_name, phone: u.phone, address: u.address }
    await api.adminUpdateUser(u.id, payload)
    alert('已保存')
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || '保存失败，请检查管理员登录或网络'
    alert(msg)
  }
}

async function loadCategories(){
  const { data } = await api.adminListCategories()
  categories.value = data
}

async function createCategory(){
  const { data } = await api.adminCreateCategory({ name: newCategory.value })
  categories.value.push(data)
  newCategory.value = ''
}

async function updateCategory(c){
  try {
    await api.adminUpdateCategory(c.id, { name: c.name })
    alert('已保存')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '保存失败')
  }
}

async function deleteCategory(c){
  if (!confirm('确认删除该类别？')) return
  await api.adminDeleteCategory(c.id)
  categories.value = categories.value.filter(x => x.id !== c.id)
}

async function loadProducts(){
  const key = (search.value || '').trim() || undefined
  const { data } = await api.adminListProducts(key, page.value, pageSize.value)
  products.value = data.items
  total.value = data.total
  page.value = data.page
  pageSize.value = data.page_size
}

function doSearch(){
  page.value = 1
  loadProducts()
}

async function createProduct(){
  const { data } = await api.adminCreateProduct(productForm)
  products.value.unshift(data)
  Object.keys(productForm).forEach(k => productForm[k] = '')
}

async function updateProduct(p){
  try {
    const payload = { name: p.name, price: p.price, stock: p.stock, category: p.category }
    await api.adminUpdateProduct(p.id, payload)
    alert('已保存')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '保存失败')
  }
}

async function onSelectImage(p, e){
  const file = e.target.files?.[0]
  if (!file) return
  const { data } = await api.adminUploadProductImage(p.id, file)
  const idx = products.value.findIndex(x => x.id === p.id)
  if (idx !== -1) products.value[idx] = data
}

async function deleteProduct(p){
  if (!confirm('确认删除该商品？')) return
  await api.adminDeleteProduct(p.id)
  products.value = products.value.filter(x => x.id !== p.id)
}

async function bulkImport(){
  try {
    const arr = JSON.parse(bulkText.value)
    const { data } = await api.adminBulkCreateProducts(arr)
    alert(`已导入 ${data.length} 条`)
    await loadProducts()
  } catch (e) {
    alert('JSON 格式错误或导入失败')
  }
}

function nextPage(){
  if (page.value < totalPages.value){
    page.value += 1
    loadProducts()
  }
}
function prevPage(){
  if (page.value > 1){
    page.value -= 1
    loadProducts()
  }
}

async function loadOrders(){
  const { data } = await api.adminListOrders()
  orders.value = data
}

async function loadChats(){
  const { data } = await api.adminListChats({ userId: chatFilter.userId || undefined, productId: chatFilter.productId || undefined, role: (chatFilter.role || '').trim() || undefined, q: (chatFilter.q || '').trim() || undefined, limit: chatFilter.limit || 100 })
  chats.value = data
}
async function deleteChat(m){ if(!confirm(`确认删除消息 #${m.id}?`)) return; await api.adminDeleteChat(m.id); chats.value = chats.value.filter(x=>x.id!==m.id) }
async function deleteConversation(){
  if(!chatFilter.userId) return alert('请填写用户ID')
  const ok = confirm(`确认删除用户#${chatFilter.userId} 与商品#${chatFilter.productId || '-'} 的整段会话？`)
  if(!ok) return
  const { data } = await api.adminDeleteConversation(chatFilter.userId, chatFilter.productId || undefined)
  alert(`已删除 ${data.deleted} 条`)
  await loadChats()
}

async function loadCoupons(){ const { data } = await api.adminListCoupons(); coupons.value = data }
async function createCoupon(){ const { data } = await api.adminCreateCoupon(couponForm); coupons.value.unshift(data); Object.keys(couponForm).forEach(k=>{ if(k==='discount_type') couponForm[k]='amount'; else if(k==='active') couponForm[k]=true; else couponForm[k]='' }) }
async function updateCoupon(c){ const payload = { discount_type: c.discount_type, discount_value: c.discount_value, min_spend: c.min_spend, active: c.active, valid_from: c.valid_from || null, valid_to: c.valid_to || null, allowed_product_id: c.allowed_product_id || null }; await api.adminUpdateCoupon(c.id, payload); alert('已保存') }
async function deleteCoupon(c){ if(!confirm('确认删除该优惠券？')) return; await api.adminDeleteCoupon(c.id); coupons.value = coupons.value.filter(x=>x.id!==c.id) }
async function assignCoupon(){
  if(!assignUserId.value || !assignCouponId.value) return alert('请填写用户ID与优惠券')
  try {
    const n = Math.max(1, +assignCount.value || 1)
    for(let i=0;i<n;i++){ await api.adminAssignCoupon(assignCouponId.value, assignUserId.value) }
    alert('已发放')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '发放失败')
  }
}
async function assignCouponBulk(){
  if(!assignCouponId.value) return alert('请选择优惠券')
  try {
    const n = Math.max(1, +assignCount.value || 1)
    await api.adminAssignCouponBulk(assignCouponId.value, { quantity: n, all_users: !!assignAllUsers.value })
    alert('已发放')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '发放失败')
  }
}

async function loadMemberships(){ const { data } = await api.adminListMemberships(); memberships.value = data }
async function createMembership(){ const uid = createMembershipUserId.value; if(!uid) return alert('请填写用户ID'); const { data } = await api.adminCreateMembership(uid, createMembershipForm); memberships.value.unshift(data) }
async function updateMembership(m){
  try {
    const payload = { level: m.level, status: m.status, plan_id: m.plan_id, extra_info: m.extra_info }
    await api.adminUpdateMembership(m.user_id, payload)
    alert('已保存')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '保存失败')
  }
}
async function deleteMembership(m){ if(!confirm('确认删除该会员？')) return; await api.adminDeleteMembership(m.user_id); memberships.value = memberships.value.filter(x=>x.id!==m.id) }
async function loadMembershipPlans(){ const { data } = await api.adminListMembershipPlans(); membershipPlans.value = data }
async function createMembershipPlan(){ const { data } = await api.adminCreateMembershipPlan(membershipPlanForm); membershipPlans.value.unshift(data); Object.keys(membershipPlanForm).forEach(k=>{ if(k==='discount_percent') membershipPlanForm[k]=10; else if(k==='active') membershipPlanForm[k]=true; else membershipPlanForm[k]='' }) }
async function updateMembershipPlan(p){
  try {
    const payload = { name: p.name, discount_percent: p.discount_percent, active: p.active }
    await api.adminUpdateMembershipPlan(p.id, payload)
    alert('已保存')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '保存失败')
  }
}
async function deleteMembershipPlan(p){ if(!confirm('确认删除该计划？')) return; await api.adminDeleteMembershipPlan(p.id); membershipPlans.value = membershipPlans.value.filter(x=>x.id!==p.id) }
async function loadMembershipCards(){ const { data } = await api.adminListMembershipCards(); membershipCards.value = data }
async function createMembershipCard(){
  try {
    creatingCard.value = true
    const payload = { card_no: membershipCardForm.card_no, plan_id: membershipCardForm.plan_id, balance: membershipCardForm.balance || 0, published: membershipCardForm.published }
    const { data } = await api.adminCreateMembershipCard(payload)
    membershipCards.value.unshift(data)
    membershipCardForm.card_no=''
    membershipCardForm.plan_id=null
    membershipCardForm.balance=0
    membershipCardForm.published=false
    alert('已创建会员卡')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '创建失败，请检查计划与卡号是否正确')
  } finally {
    creatingCard.value = false
  }
}
async function updateMembershipCard(c){
  try {
    const payload = { user_id: c.user_id, balance: c.balance, status: c.status, published: c.published }
    await api.adminUpdateMembershipCard(c.id, payload)
    alert('已保存')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '保存失败')
  }
}
async function deleteMembershipCard(c){ if(!confirm('确认删除该会员卡？')) return; await api.adminDeleteMembershipCard(c.id); membershipCards.value = membershipCards.value.filter(x=>x.id!==c.id) }

function onPlanLevelChange(){
  const lv = membershipPlanLevel.value
  const ts = Date.now()
  if (lv === 'premium'){
    membershipPlanForm.code = `premium_${ts}`
    membershipPlanForm.name = '高级会员计划'
    membershipPlanForm.discount_percent = 15
  } else if (lv === 'plus'){
    membershipPlanForm.code = `plus_${ts}`
    membershipPlanForm.name = '中级会员计划'
    membershipPlanForm.discount_percent = 10
  } else {
    membershipPlanForm.code = `standard_${ts}`
    membershipPlanForm.name = '标准会员计划'
    membershipPlanForm.discount_percent = 5
  }
}

function planLevel(p){
  const code = (p.code||'').toLowerCase()
  const name = (p.name||'')
  if (code.includes('premium') || name.includes('高级')) return '高级'
  if (code.includes('plus') || name.includes('中级')) return '中级'
  return '标准'
}

async function updateOrderStatus(o){
  try {
    await api.adminUpdateOrderStatus(o.id, o.status)
    alert('已保存状态')
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || '保存失败，请检查管理员登录或网络'
    alert(msg)
  }
}

async function updateLogistics(o){
  try {
    await api.adminUpdateLogistics(o.id, o.shipping.status, o.shipping.tracking_number || undefined)
    await loadOrders()
    alert('已保存物流并已刷新列表')
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || '保存失败，请检查管理员登录或网络'
    alert(msg)
  }
}

const loaded = reactive({ stats:false, stock:false, reviews:false, users:false, categories:false, products:false, orders:false, chats:false, coupons:false, memberships:false, membershipPlans:false, membershipCards:false, knowledge:false, cache:false, logs:false })
function loadForTab(tab){
  if (!authed.value) return
  if (tab === 'stats' && !loaded.stats){ loaded.stats = true; loadDashboardStats() }
  if (tab === 'stock' && !loaded.stock){ loaded.stock = true; loadStockAlerts(); loadStockStatistics() }
  if (tab === 'reviews' && !loaded.reviews){ loaded.reviews = true; loadReviews() }
  if (tab === 'cache' && !loaded.cache){ loaded.cache = true; loadCacheStatus() }
  if (tab === 'logs' && !loaded.logs){ loaded.logs = true; loadLogFiles(); loadLogStats() }
  if (tab === 'users' && !loaded.users){ loaded.users = true; loadUsers() }
  if (tab === 'categories' && !loaded.categories){ loaded.categories = true; loadCategories() }
  if (tab === 'products' && !loaded.products){ loaded.products = true; loadProducts() }
  if (tab === 'orders' && !loaded.orders){ loaded.orders = true; loadOrders() }
  if (tab === 'chats' && !loaded.chats){ loaded.chats = true; loadChats() }
  if (tab === 'coupons' && !loaded.coupons){ loaded.coupons = true; loadCoupons(); loadAutoIssueRules() }
  if (tab === 'memberships' && !loaded.memberships){ loaded.memberships = true; loadMemberships() }
  if (tab === 'memberships' && !loaded.membershipPlans){ loaded.membershipPlans = true; loadMembershipPlans() }
  if (tab === 'memberships' && !loaded.membershipCards){ loaded.membershipCards = true; loadMembershipCards() }
  if (tab === 'knowledge' && !loaded.knowledge){ loaded.knowledge = true; loadKnowledgeDocuments() }
}

// 知识库管理函数
async function loadKnowledgeDocuments(){
  try {
    const { data } = await api.knowledgeListDocuments(
      knowledgeFilter.category || undefined,
      knowledgeFilter.active
    )
    knowledgeDocuments.value = data
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '加载失败')
  }
}

async function createKnowledgeDocument(){
  try {
    const payload = {
      title: knowledgeForm.title,
      content: knowledgeForm.content,
      category: knowledgeForm.category || null,
      tags: knowledgeForm.tags || null
    }
    const { data } = await api.knowledgeCreateDocument(payload)
    knowledgeDocuments.value.unshift(data)
    Object.keys(knowledgeForm).forEach(k => knowledgeForm[k] = '')
    alert('文档已创建并完成向量化，已添加到知识库')
    // 刷新列表以确保显示最新数据
    await loadKnowledgeDocuments()
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '创建失败')
  }
}

async function updateKnowledgeDocument(doc){
  try {
    const payload = { active: doc.active }
    await api.knowledgeUpdateDocument(doc.id, payload)
    alert('已保存')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '保存失败')
  }
}

async function deleteKnowledgeDocument(doc){
  if (!confirm(`确认删除文档 "${doc.title}"？`)) return
  try {
    await api.knowledgeDeleteDocument(doc.id)
    knowledgeDocuments.value = knowledgeDocuments.value.filter(x => x.id !== doc.id)
    alert('已删除')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '删除失败')
  }
}

async function viewKnowledgeDocument(doc){
  try {
    const { data } = await api.knowledgeGetDocument(doc.id)
    alert(`标题：${data.title}\n\n内容：${data.content.substring(0, 500)}${data.content.length > 500 ? '...' : ''}\n\n块数：${data.chunk_count}\n质量评分：${data.quality_score ? data.quality_score.toFixed(2) : '-'}`)
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '查看失败')
  }
}

async function importFromDatabase(){
  try {
    const payload = {
      table_name: dbImportForm.table_name,
      title: dbImportForm.title || null,
      category: dbImportForm.category || null,
      limit: dbImportForm.limit || 1000,
      columns: dbImportForm.columns ? dbImportForm.columns.split(',').map(s => s.trim()) : null
    }
    const { data } = await api.knowledgeImportFromDatabase(payload)
    knowledgeDocuments.value.unshift(data)
    Object.keys(dbImportForm).forEach(k => {
      if (k === 'limit') dbImportForm[k] = 1000
      else dbImportForm[k] = ''
    })
    alert(`已从数据库表 "${payload.table_name}" 导入文档并完成向量化`)
    // 刷新列表以确保显示最新数据
    await loadKnowledgeDocuments()
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '导入失败')
  }
}

async function importFromUrl(){
  try {
    const payload = {
      url: urlImportForm.url,
      title: urlImportForm.title || null,
      category: urlImportForm.category || null
    }
    const { data } = await api.knowledgeImportFromUrl(payload)
    knowledgeDocuments.value.unshift(data)
    Object.keys(urlImportForm).forEach(k => urlImportForm[k] = '')
    alert('已从URL导入文档并完成向量化')
    // 刷新列表以确保显示最新数据
    await loadKnowledgeDocuments()
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '导入失败')
  }
}

function onKnowledgeFileSelect(e){
  selectedFile.value = e.target.files?.[0] || null
}

async function uploadKnowledgeFile(){
  if (!selectedFile.value) return alert('请选择文件')
  
  const fileName = selectedFile.value.name
  const fileSize = (selectedFile.value.size / 1024 / 1024).toFixed(2) + 'MB'
  
  // 显示上传提示
  if (!confirm(`准备上传文件：${fileName} (${fileSize})\n\n文档解析和向量化可能需要较长时间，请耐心等待。\n\n确定继续吗？`)) {
    return
  }
  
  try {
    // 显示加载提示
    const loadingMsg = `正在上传并处理文件：${fileName}\n\n这可能需要几十秒到几分钟，请勿关闭页面...`
    alert(loadingMsg)
    
    const { data } = await api.knowledgeUploadDocument(
      selectedFile.value, 
      undefined,  // title
      fileUploadCategory.value || undefined,  // category
      undefined   // tags
    )
    
    // 清空文件选择
    selectedFile.value = null
    fileUploadCategory.value = ''
    const fileInput = document.querySelector('input[type="file"]')
    if (fileInput) fileInput.value = ''
    
    // 刷新列表
    await loadKnowledgeDocuments()
    
    alert(`✓ 文件已成功上传并完成向量化！\n\n文档ID: ${data.id}\n标题: ${data.title}\n块数: ${data.chunk_count}\n质量评分: ${data.quality_score ? data.quality_score.toFixed(2) : 'N/A'}`)
  } catch (e) {
    let errorMsg = '上传失败'
    if (e?.code === 'ECONNABORTED' || e?.message?.includes('timeout')) {
      errorMsg = '上传超时：文件处理时间过长。\n\n可能原因：\n1. 文件过大\n2. 文档解析耗时（特别是PDF和图片OCR）\n3. 向量化处理耗时\n\n建议：\n- 尝试上传较小的文件\n- 或等待更长时间后重试'
    } else if (e?.response?.data?.detail) {
      errorMsg = `上传失败：${e.response.data.detail}`
    } else if (e?.message) {
      errorMsg = `上传失败：${e.message}`
    }
    alert(errorMsg)
    console.error('上传错误详情：', e)
  }
}

async function searchKnowledge(){
  if (!knowledgeSearchQuery.value.trim()) return alert('请输入查询内容')
  try {
    const { data } = await api.knowledgeSearch(
      knowledgeSearchQuery.value,
      knowledgeSearchTopK.value || 5,
      knowledgeFilter.category || undefined
    )
    knowledgeSearchResults.value = data
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '搜索失败')
  }
}

async function rebuildKnowledgeIndex(){
  if (!confirm('确认重建向量索引？这可能需要一些时间。')) return
  try {
    await api.knowledgeRebuildIndex()
    alert('索引重建完成')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '重建失败')
  }
}

onMounted(() => {
  api.initAdminAuthFromSession()
  // 初始化时不要自动检查状态，避免在没有认证时发送请求
  authed.value = false
  statusText.value = '请先登录管理员'
  
  // 如果有认证信息，延迟检查（给认证头设置时间）
  setTimeout(() => {
    try {
      const hasAuth = sessionStorage.getItem('admin_basic') || api.adminHttp?.defaults?.headers?.common?.Authorization
      if (hasAuth) {
        checkStatus().then(() => { 
          if (authed.value) {
            loadForTab(active.value) 
          }
        }).catch(() => {
          // 如果检查失败，清除无效的认证信息
          api.clearAdminAuth()
        })
      }
    } catch {
      // 忽略错误
    }
  }, 100)
})
watch(active, (tab) => { loadForTab(tab) })
</script>

<style scoped>
.admin { display: grid; gap: 16px; }
.card { background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 16px; }
.row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.list .row-users { display: grid; grid-template-columns: 2fr 1fr 1fr 2fr 1.4fr auto; align-items: center; }
.list .row-products { display: grid; grid-template-columns: 60px 1.4fr 0.8fr 0.8fr 1fr auto 56px 1.4fr auto auto; align-items: center; }
.card ul .row-orders { display: grid; grid-template-columns: 2fr 1.6fr 1fr auto 1fr 1fr auto 0.8fr 1.2fr; align-items: center; }
.list .row-coupons { display: grid; grid-template-columns: 1.2fr 0.9fr 0.8fr 0.9fr 1.6fr 0.9fr 1fr auto auto; align-items: center; }
.memberships-list .row-memberships { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1.4fr auto auto; align-items: center; }
.memberships-list .row-memberships .btn { min-width: 84px; justify-self: start; }
.memberships-list .row-memberships input, .memberships-list .row-memberships select { min-width: 140px; }
.card ul .row-plan { display: grid; grid-template-columns: 1.5fr 1.4fr 1fr 0.8fr 0.8fr 1.4fr auto; align-items: center; }
.card ul .row-card { display: grid; grid-template-columns: 2fr 1fr 1fr 0.8fr 1fr auto auto; align-items: center; }
.row-knowledge { display: grid; grid-template-columns: 2fr 1fr 0.8fr 0.6fr 0.8fr 0.8fr 1.2fr; align-items: center; }
.mono { font-family: monospace; font-size: 0.9em; }
.pager { justify-content: center; width: 100%; }
.pager { justify-content: center; width: 100%; }
.row-nowrap { flex-wrap: nowrap; overflow-x: auto; }
.row input, .row select { height: 36px; padding: 0 10px; }
.btn { height: 36px; padding: 0 12px; border: none; border-radius: 6px; background: #1d4ed8; color: #fff; cursor: pointer; display: inline-flex; align-items: center; }
.btn.outline { background: #fff; border: 1px solid #1d4ed8; color: #1d4ed8; }
.btn.danger { background: #ef4444; }
.tabs { display: flex; gap: 8px; }
.tab { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; background: #f9fafb; cursor: pointer; }
.tab.active { background: #1d4ed8; color: #fff; border-color: #1d4ed8; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 12px 0; }
.kpi { background: #f3f4f6; padding: 12px; border-radius: 8px; }
textarea { flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 6px; min-width: 360px; }
.header { font-weight: 600; color: #374151; }
.hint { margin: 6px 0 12px; color: #6b7280; }
</style>