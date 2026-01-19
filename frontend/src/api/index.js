import axios from "axios";

const http = axios.create({
  baseURL: "/api",
  timeout: 180000, // 增加到 180 秒（3分钟），用于 AI 模型调用
});
const adminHttp = axios.create({
  baseURL: "/adminapi",
  timeout: 30000,  // 管理员接口增加到30秒，因为统计查询可能需要更长时间
});

export const api = {
  // 导出 adminHttp 以便在组件中访问
  adminHttp,
  getProducts(search, category, page = 1, pageSize = 10) {
    const params = { page, page_size: pageSize };
    if (search) params.search = search;
    if (category) params.category = category;
    return http.get("/products/", { params });
  },
  getCategories() {
    return http.get("/products/categories");
  },
  // 已停用：批量生成商品
  // seedProducts(count = 50) {
  //   return http.post(`/products/seed`, null, { params: { count } });
  // },
  getCart(userId) {
    return http.get(`/carts/${userId}`);
  },
  addToCart(userId, payload) {
    return http.post(`/carts/${userId}/items`, payload);
  },
  updateCartItem(userId, itemId, payload) {
    return http.put(`/carts/${userId}/items/${itemId}`, payload);
  },
  removeCartItem(userId, itemId) {
    return http.delete(`/carts/${userId}/items/${itemId}`);
  },
  clearCart(userId) {
    return http.delete(`/carts/${userId}/items`);
  },
  createOrder(userId, payload) {
    return http.post(`/orders/${userId}`, payload);
  },
  getOrders(userId) {
    return http.get(`/orders/${userId}`);
  },
  deleteOrder(userId, orderId){
    return http.delete(`/orders/${userId}/${orderId}`)
  },
  getProduct(productId) {
    return http.get(`/products/${productId}`);
  },
  getOrderDetail(orderId) {
    return http.get(`/orders/detail/${orderId}`);
  },
  getLogistics(orderId) {
    return http.get(`/logistics/${orderId}`);
  },
  getCustomerService(productId) {
    return http.get(`/products/${productId}/customer-service`);
  },
  // 客服聊天
  sendChat(userId, productId, message, model){
    const payload = { user_id: userId, product_id: productId, message }
    if (model) payload.model = model
    return http.post(`/customer-service/chat`, payload, { timeout: 300000 }) // 5分钟超时，首次加载RAG模型需要较长时间
  },
  getChatHistory(userId, productId, { start, end, limit } = {}){
    const params = {}
    if (start) params.start = start
    if (end) params.end = end
    if (limit != null) params.limit = limit
    return http.get(`/customer-service/history/${userId}/${productId}`, { params })
  },
  getAIStatus(){
    return http.get(`/customer-service/status`)
  },
  clearChat(userId, productId){
    return http.delete(`/customer-service/history/${userId}/${productId}`)
  },
  // 商品评价
  createReview(productId, userId, payload) {
    return http.post(`/reviews/products/${productId}/users/${userId}`, payload);
  },
  getProductReviews(productId, status = 'approved', page = 1, pageSize = 10) {
    return http.get(`/reviews/products/${productId}`, { params: { status, page, page_size: pageSize } });
  },
  getProductReviewStats(productId) {
    return http.get(`/reviews/products/${productId}/stats`);
  },
  getReview(reviewId) {
    return http.get(`/reviews/${reviewId}`);
  },
  // 用户自己的评价
  getUserReviews(userId, status, page = 1, pageSize = 10) {
    const params = { page, page_size: pageSize };
    if (status) params.status = status;
    return http.get(`/reviews/users/${userId}`, { params });
  },
  updateReview(reviewId, userId, payload) {
    return http.put(`/reviews/${reviewId}/users/${userId}`, payload);
  },
  deleteReview(reviewId, userId) {
    return http.delete(`/reviews/${reviewId}/users/${userId}`);
  },
  retractChatMessage(messageId, userId){
    return http.delete(`/customer-service/message/${messageId}`, { params: { user_id: userId }})
  },
  sendChatWithUpload(userId, productId, message, { images = [], files = [], audios = [] } = {}, model){
    const fd = new FormData()
    fd.append('user_id', userId)
    if (productId != null) fd.append('product_id', productId)
    fd.append('message', message || '')
    images.forEach(f => fd.append('images', f))
    files.forEach(f => fd.append('files', f))
    audios.forEach(f => fd.append('audios', f))
    if (model) fd.append('model', model)
    return http.post(`/customer-service/chat/upload`, fd, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 300000 }) // 5分钟超时
  },
  getUser(userId) {
    return http.get(`/users/${userId}`);
  },
  registerUser(payload) {
    return http.post(`/users/register`, payload);
  },
  login(payload) {
    return http.post(`/users/login`, payload);
  },
  updateUser(userId, payload) {
    return http.put(`/users/${userId}`, payload);
  },
  deleteUser(userId) {
    return http.delete(`/users/${userId}`);
  },
  // 地址簿
  listAddresses(userId) {
    return http.get(`/addresses/${userId}`);
  },
  createAddress(userId, payload) {
    return http.post(`/addresses/${userId}`, payload);
  },
  updateAddress(userId, addressId, payload) {
    return http.put(`/addresses/${userId}/${addressId}`, payload);
  },
  deleteAddress(userId, addressId) {
    return http.delete(`/addresses/${userId}/${addressId}`);
  },

  // 会员
  getMembership(userId){
    return http.get(`/memberships/${userId}`);
  },
  createMembership(userId, payload){
    return http.post(`/memberships/${userId}`, payload);
  },
  updateMembership(userId, payload){
    return http.put(`/memberships/${userId}`, payload);
  },
  rechargeMembership(userId, amount){
    return http.post(`/memberships/${userId}/recharge`, { amount });
  },
  listMembershipPlans(){
    return http.get(`/memberships/plans`);
  },
  listPublishedMembershipCards(){
    return http.get(`/memberships/cards/published`);
  },
  listMyMembershipCards(userId){
    return http.get(`/memberships/${userId}/cards`);
  },

  // 优惠券
  listUserCoupons(userId){
    return http.get(`/coupons/${userId}`);
  },
  adminAssignCouponBulk(couponId, payload){
    return http.post(`/admin/coupons/${couponId}/assign/bulk`, payload);
  },

  setAdminAuth(username, password){
    const u = String(username || '').trim()
    const p = String(password || '').trim()
    const token = btoa(`${u}:${p}`)
    const basic = `Basic ${token}`
    adminHttp.defaults.headers.common["Authorization"] = basic
    try { sessionStorage.setItem('admin_basic', basic) } catch {}
  },
  setAdminToken(basicToken){
    adminHttp.defaults.headers.common["Authorization"] = basicToken
  },
  initAdminAuthFromSession(){
    try {
      const basic = sessionStorage.getItem('admin_basic')
      if (basic) adminHttp.defaults.headers.common["Authorization"] = basic
    } catch {}
  },
  adminStatus(){
    return adminHttp.get(`/status`)
  },
  adminListUsers(){
    return adminHttp.get(`/users`)
  },
  adminCreateUser(payload){
    return adminHttp.post(`/users`, payload)
  },
  adminUpdateUser(userId, payload){
    return adminHttp.put(`/users/${userId}`, payload)
  },
  adminListCategories(){
    return adminHttp.get(`/categories`)
  },
  adminCreateCategory(payload){
    return adminHttp.post(`/categories`, payload)
  },
  adminUpdateCategory(id, payload){
    return adminHttp.put(`/categories/${id}`, payload)
  },
  adminDeleteCategory(id){
    return adminHttp.delete(`/categories/${id}`)
  },
  adminListProducts(search, page=1, pageSize=20){
    const params = { search, page, page_size: pageSize }
    return adminHttp.get(`/products`, { params })
  },
  adminCreateProduct(payload){
    return adminHttp.post(`/products`, payload)
  },
  adminUpdateProduct(id, payload){
    return adminHttp.put(`/products/${id}`, payload)
  },
  adminUploadProductImage(id, file){
    const fd = new FormData()
    fd.append('file', file)
    return adminHttp.post(`/products/${id}/image`, fd)
  },
  adminDeleteProduct(id){
    return adminHttp.delete(`/products/${id}`)
  },
  adminBulkCreateProducts(items){
    return adminHttp.post(`/products/bulk`, items)
  },
  adminListOrders(){
    return adminHttp.get(`/orders`)
  },
  adminUpdateOrderStatus(id, statusValue){
    return adminHttp.put(`/orders/${id}/status`, null, { params: { status_value: statusValue }})
  },
  adminUpdateLogistics(orderId, statusValue, tracking){
    const params = { status_value: statusValue }
    if (tracking) params.tracking_number = tracking
    return adminHttp.put(`/logistics/${orderId}`, null, { params })
  },
  adminStats(){
    return adminHttp.get(`/stats`)
  },
  // 管理员：统计数据
  adminGetDashboardStats(){
    return adminHttp.get(`/statistics/dashboard`)
  },
  adminGetSalesStatistics(days = 30){
    return adminHttp.get(`/statistics/sales`, { params: { days } })
  },
  adminGetProductStatistics(){
    return adminHttp.get(`/statistics/products`)
  },
  adminGetUserStatistics(){
    return adminHttp.get(`/statistics/users`)
  },
  // 管理员：库存预警
  adminGetStockAlerts(threshold = 10){
    return adminHttp.get(`/stock-alerts`, { params: { threshold } })
  },
  adminGetStockStatistics(threshold = null){
    const params = threshold !== null ? { threshold } : {}
    return adminHttp.get(`/stock-alerts/statistics`, { params })
  },
  // 管理员：评价管理
  adminListReviews(productId, status, page = 1, pageSize = 20){
    const params = { page, page_size: pageSize }
    if (productId) params.product_id = productId
    if (status) params.status = status
    return adminHttp.get(`/reviews`, { params })
  },
  adminDeleteReview(reviewId){
    return adminHttp.delete(`/reviews/${reviewId}`)
  },
  adminListChats({ userId, productId, role, q, limit }={}){
    const params = {}
    if (userId != null) params.user_id = userId
    if (productId != null) params.product_id = productId
    if (role) params.role = role
    if (q) params.q = q
    if (limit != null) params.limit = limit
    return adminHttp.get(`/chats`, { params })
  },
  adminDeleteChat(id){
    return adminHttp.delete(`/chats/${id}`)
  },
  adminDeleteConversation(userId, productId){
    const params = { user_id: userId }
    if (productId != null) params.product_id = productId
    return adminHttp.delete(`/chats/conversation`, { params })
  },
  // 管理员：优惠券与会员
  adminListCoupons(){
    return adminHttp.get(`/coupons`)
  },
  adminCreateCoupon(payload){
    return adminHttp.post(`/coupons`, payload)
  },
  adminUpdateCoupon(id, payload){
    return adminHttp.put(`/coupons/${id}`, payload)
  },
  adminDeleteCoupon(id){
    return adminHttp.delete(`/coupons/${id}`)
  },
  adminAssignCoupon(couponId, userId){
    return adminHttp.post(`/coupons/${couponId}/assign/${userId}`)
  },
  adminListMemberships(){
    return adminHttp.get(`/memberships`)
  },
  adminListMembershipPlans(){
    return adminHttp.get(`/membership-plans`)
  },
  adminCreateMembershipPlan(payload){
    return adminHttp.post(`/membership-plans`, payload)
  },
  adminUpdateMembershipPlan(id, payload){
    return adminHttp.put(`/membership-plans/${id}`, payload)
  },
  adminDeleteMembershipPlan(id){
    return adminHttp.delete(`/membership-plans/${id}`)
  },
  adminListMembershipCards(){
    return adminHttp.get(`/membership-cards`)
  },
  adminCreateMembershipCard(payload){
    return adminHttp.post(`/membership-cards`, payload)
  },
  adminUpdateMembershipCard(id, payload){
    return adminHttp.put(`/membership-cards/${id}`, payload)
  },
  adminDeleteMembershipCard(id){
    return adminHttp.delete(`/membership-cards/${id}`)
  },
  adminCreateMembership(userId, payload){
    return adminHttp.post(`/memberships/${userId}`, payload)
  },
  adminUpdateMembership(userId, payload){
    return adminHttp.put(`/memberships/${userId}`, payload)
  },
  adminDeleteMembership(userId){
    return adminHttp.delete(`/memberships/${userId}`)
  },
  // 知识库管理
  knowledgeListDocuments(category, active){
    const params = {}
    if (category && category.trim()) params.category = category.trim()
    // 只有当 active 是明确的布尔值时才传递，undefined/null 不传递（表示全部状态）
    if (active === true || active === false) {
      params.active = active
    }
    return adminHttp.get(`/knowledge-base/documents`, { params })
  },
  knowledgeCreateDocument(payload){
    return adminHttp.post(`/knowledge-base/documents`, payload)
  },
  knowledgeGetDocument(id){
    return adminHttp.get(`/knowledge-base/documents/${id}`)
  },
  knowledgeUpdateDocument(id, payload){
    return adminHttp.put(`/knowledge-base/documents/${id}`, payload)
  },
  knowledgeDeleteDocument(id){
    return adminHttp.delete(`/knowledge-base/documents/${id}`)
  },
  knowledgeGetDocumentChunks(id){
    return adminHttp.get(`/knowledge-base/documents/${id}/chunks`)
  },
  knowledgeUploadDocument(file, title, category, tags){
    const formData = new FormData()
    formData.append('file', file)
    if (title) formData.append('title', title)
    if (category) formData.append('category', category)
    if (tags) formData.append('tags', tags)
    return adminHttp.post(`/knowledge-base/documents/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000  // 120秒超时，因为文档解析和向量化可能需要较长时间
    })
  },
  knowledgeImportFromUrl(payload){
    return adminHttp.post(`/knowledge-base/documents/from-url`, payload)
  },
  knowledgeImportFromDatabase(payload){
    return adminHttp.post(`/knowledge-base/documents/from-database`, payload)
  },
  knowledgeSearch(query, topK, category){
    const params = { query, top_k: topK || 5 }
    if (category) params.category = category
    return adminHttp.post(`/knowledge-base/search`, null, { params })
  },
  knowledgeRebuildIndex(){
    return adminHttp.post(`/knowledge-base/rebuild-index`)
  },
  // Redis 缓存管理
  adminGetCacheStatus(){
    return adminHttp.get(`/cache/status`)
  },
  adminClearCache(){
    return adminHttp.post(`/cache/clear`)
  },
  adminDeleteCachePattern(pattern){
    return adminHttp.delete(`/cache/${pattern}`)
  },
  // 优惠券自动发放规则管理
  adminGetAutoIssueRules(){
    return adminHttp.get(`/coupons/auto-issue/rules`)
  },
  adminCreateAutoIssueRule(payload){
    return adminHttp.post(`/coupons/auto-issue/rules`, payload)
  },
  adminUpdateAutoIssueRule(ruleId, payload){
    return adminHttp.put(`/coupons/auto-issue/rules/${ruleId}`, payload)
  },
  adminDeleteAutoIssueRule(ruleId){
    return adminHttp.delete(`/coupons/auto-issue/rules/${ruleId}`)
  },
  adminSetAutoIssueConfig(payload){
    return adminHttp.post(`/coupons/auto-issue/config`, payload)
  },
  // 日志查看
  adminListLogFiles(){
    return adminHttp.get(`/logs/files`)
  },
  adminGetLogStats(){
    return adminHttp.get(`/logs/stats`)
  },
  adminReadLogFile(filename, lines = 1000, level = null, search = null, reverse = true){
    const params = { lines, reverse }
    if (level) params.level = level
    if (search) params.search = search
    return adminHttp.get(`/logs/read/${filename}`, { params })
  },
  adminClearLogFile(filename){
    return adminHttp.delete(`/logs/clear/${filename}`)
  },
  clearAdminAuth(){
    delete adminHttp.defaults.headers.common["Authorization"]
    try { sessionStorage.removeItem('admin_basic') } catch {}
  }
};

