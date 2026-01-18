import axios from "axios";

const http = axios.create({
  baseURL: "/api",
  timeout: 8000,
});
const adminHttp = axios.create({
  baseURL: "/adminapi",
  timeout: 8000,
});

export const api = {
  getProducts(search, category, page = 1, pageSize = 10) {
    const params = { page, page_size: pageSize };
    if (search) params.search = search;
    if (category) params.category = category;
    return http.get("/products", { params });
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
    return http.post(`/customer-service/chat`, payload, { timeout: 120000 }) // 120秒超时，因为AI回复可能需要较长时间
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
    return http.post(`/customer-service/chat/upload`, fd, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 60000 })
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
    return adminHttp.get(`/admin/status`)
  },
  adminListUsers(){
    return adminHttp.get(`/admin/users`)
  },
  adminCreateUser(payload){
    return adminHttp.post(`/admin/users`, payload)
  },
  adminUpdateUser(userId, payload){
    return adminHttp.put(`/admin/users/${userId}`, payload)
  },
  adminListCategories(){
    return adminHttp.get(`/admin/categories`)
  },
  adminCreateCategory(payload){
    return adminHttp.post(`/admin/categories`, payload)
  },
  adminUpdateCategory(id, payload){
    return adminHttp.put(`/admin/categories/${id}`, payload)
  },
  adminDeleteCategory(id){
    return adminHttp.delete(`/admin/categories/${id}`)
  },
  adminListProducts(search, page=1, pageSize=20){
    const params = { search, page, page_size: pageSize }
    return adminHttp.get(`/admin/products`, { params })
  },
  adminCreateProduct(payload){
    return adminHttp.post(`/admin/products`, payload)
  },
  adminUpdateProduct(id, payload){
    return adminHttp.put(`/admin/products/${id}`, payload)
  },
  adminUploadProductImage(id, file){
    const fd = new FormData()
    fd.append('file', file)
    return adminHttp.post(`/admin/products/${id}/image`, fd)
  },
  adminDeleteProduct(id){
    return adminHttp.delete(`/admin/products/${id}`)
  },
  adminBulkCreateProducts(items){
    return adminHttp.post(`/admin/products/bulk`, items)
  },
  adminListOrders(){
    return adminHttp.get(`/admin/orders`)
  },
  adminUpdateOrderStatus(id, statusValue){
    return adminHttp.put(`/admin/orders/${id}/status`, null, { params: { status_value: statusValue }})
  },
  adminUpdateLogistics(orderId, statusValue, tracking){
    const params = { status_value: statusValue }
    if (tracking) params.tracking_number = tracking
    return adminHttp.put(`/admin/logistics/${orderId}`, null, { params })
  },
  adminStats(){
    return adminHttp.get(`/admin/stats`)
  },
  adminListChats({ userId, productId, role, q, limit }={}){
    const params = {}
    if (userId != null) params.user_id = userId
    if (productId != null) params.product_id = productId
    if (role) params.role = role
    if (q) params.q = q
    if (limit != null) params.limit = limit
    return adminHttp.get(`/admin/chats`, { params })
  },
  adminDeleteChat(id){
    return adminHttp.delete(`/admin/chats/${id}`)
  },
  adminDeleteConversation(userId, productId){
    const params = { user_id: userId }
    if (productId != null) params.product_id = productId
    return adminHttp.delete(`/admin/chats/conversation`, { params })
  },
  // 管理员：优惠券与会员
  adminListCoupons(){
    return adminHttp.get(`/admin/coupons`)
  },
  adminCreateCoupon(payload){
    return adminHttp.post(`/admin/coupons`, payload)
  },
  adminUpdateCoupon(id, payload){
    return adminHttp.put(`/admin/coupons/${id}`, payload)
  },
  adminDeleteCoupon(id){
    return adminHttp.delete(`/admin/coupons/${id}`)
  },
  adminAssignCoupon(couponId, userId){
    return adminHttp.post(`/admin/coupons/${couponId}/assign/${userId}`)
  },
  adminListMemberships(){
    return adminHttp.get(`/admin/memberships`)
  },
  adminListMembershipPlans(){
    return adminHttp.get(`/admin/membership-plans`)
  },
  adminCreateMembershipPlan(payload){
    return adminHttp.post(`/admin/membership-plans`, payload)
  },
  adminUpdateMembershipPlan(id, payload){
    return adminHttp.put(`/admin/membership-plans/${id}`, payload)
  },
  adminDeleteMembershipPlan(id){
    return adminHttp.delete(`/admin/membership-plans/${id}`)
  },
  adminListMembershipCards(){
    return adminHttp.get(`/admin/membership-cards`)
  },
  adminCreateMembershipCard(payload){
    return adminHttp.post(`/admin/membership-cards`, payload)
  },
  adminUpdateMembershipCard(id, payload){
    return adminHttp.put(`/admin/membership-cards/${id}`, payload)
  },
  adminDeleteMembershipCard(id){
    return adminHttp.delete(`/admin/membership-cards/${id}`)
  },
  adminCreateMembership(userId, payload){
    return adminHttp.post(`/admin/memberships/${userId}`, payload)
  },
  adminUpdateMembership(userId, payload){
    return adminHttp.put(`/admin/memberships/${userId}`, payload)
  },
  adminDeleteMembership(userId){
    return adminHttp.delete(`/admin/memberships/${userId}`)
  },
  // 知识库管理
  knowledgeListDocuments(category, active){
    const params = {}
    if (category) params.category = category
    if (active !== undefined) params.active = active
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
  clearAdminAuth(){
    delete adminHttp.defaults.headers.common["Authorization"]
    try { sessionStorage.removeItem('admin_basic') } catch {}
  }
};

