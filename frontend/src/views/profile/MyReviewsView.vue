<template>
  <div class="my-reviews">
    <h2>我的评价</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="!reviewsList.items || reviewsList.items.length === 0" class="empty">
      暂无评价
    </div>
    <div v-else>
      <div class="filter-bar">
        <select v-model="filterStatus" @change="loadMyReviews(1)">
          <option value="">全部状态</option>
          <option value="pending">待审核</option>
          <option value="approved">已通过</option>
          <option value="rejected">已拒绝</option>
        </select>
        <button class="btn" @click="loadMyReviews(1)">刷新</button>
      </div>
      
      <div class="reviews-container">
        <div v-for="review in reviewsList.items" :key="review.id" class="review-card">
          <div class="review-header">
            <div class="review-product">
              <router-link :to="{ name: 'product-detail', params: { id: review.product_id } }" class="product-link">
                {{ review.product?.name || `商品ID: ${review.product_id}` }}
              </router-link>
            </div>
            <div class="review-meta">
              <span class="rating">⭐ {{ review.rating }}</span>
              <span class="status" :class="review.status">{{ statusLabel(review.status) }}</span>
              <span class="date">{{ formatDate(review.created_at) }}</span>
              <span v-if="review.verified_purchase" class="verified-badge">已购买</span>
            </div>
          </div>
          
          <div class="review-content">
            <p class="comment">{{ review.comment || '无评价内容' }}</p>
            <div v-if="review.images_list && review.images_list.length > 0" class="review-images">
              <img v-for="(img, idx) in review.images_list" :key="idx" :src="img" :alt="`评价图片${idx+1}`" class="review-image" />
            </div>
          </div>
          
          <div class="review-actions">
            <button class="btn outline" @click="editReview(review)">编辑</button>
            <button class="btn danger" @click="deleteReview(review)">删除</button>
          </div>
        </div>
      </div>
      
      <!-- 分页 -->
      <div v-if="reviewsList.total > reviewsList.page_size" class="pagination">
        <button @click="loadMyReviews(reviewsList.page - 1)" :disabled="reviewsList.page <= 1">上一页</button>
        <span>第 {{ reviewsList.page }} / {{ Math.ceil(reviewsList.total / reviewsList.page_size) }} 页</span>
        <button @click="loadMyReviews(reviewsList.page + 1)" :disabled="reviewsList.page >= Math.ceil(reviewsList.total / reviewsList.page_size)">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const reviewsList = ref({ items: [], total: 0, page: 1, page_size: 10 })
const filterStatus = ref('')

const statusMap = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }

function statusLabel(status) { return statusMap[status] || status }

function formatDate(d) {
  try {
    if (!d) return '-'
    return new Date(d).toLocaleString()
  } catch {
    return String(d) || '-'
  }
}

async function loadMyReviews(page = 1) {
  if (!userStore.userId) {
    router.replace('/login')
    return
  }
  
  loading.value = true
  try {
    const { data } = await api.getUserReviews(userStore.userId, filterStatus.value || undefined, page, 10)
    reviewsList.value = data
    
    // 解析图片JSON
    if (data.items) {
      data.items.forEach(item => {
        if (item.images) {
          try {
            item.images_list = JSON.parse(item.images)
          } catch {
            item.images_list = []
          }
        } else {
          item.images_list = []
        }
      })
    }
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '加载评价失败')
  } finally {
    loading.value = false
  }
}

function editReview(review) {
  // 跳转到商品详情页，可以修改评价
  router.push({ name: 'product-detail', params: { id: review.product_id } })
}

async function deleteReview(review) {
  if (!confirm(`确认删除对"${review.product?.name || '该商品'}"的评价？`)) return
  
  try {
    await api.deleteReview(review.id, userStore.userId)
    alert('删除成功')
    await loadMyReviews(reviewsList.value.page)
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '删除失败')
  }
}

onMounted(() => {
  if (!userStore.userId) {
    router.replace('/login')
    return
  }
  loadMyReviews()
})
</script>

<style scoped>
.my-reviews { max-width: 900px; margin: 24px auto; padding: 24px; }
.loading, .empty { padding: 32px; text-align: center; background: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.filter-bar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; }
.filter-bar select { padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; }
.reviews-container { display: flex; flex-direction: column; gap: 16px; }
.review-card { background: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); padding: 16px; }
.review-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
.review-product { flex: 1; }
.product-link { color: #2563eb; font-weight: 600; text-decoration: none; }
.product-link:hover { text-decoration: underline; }
.review-meta { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; font-size: 14px; }
.rating { color: #f59e0b; font-weight: 600; }
.status { padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.status.pending { background: #fef3c7; color: #92400e; }
.status.approved { background: #d1fae5; color: #065f46; }
.status.rejected { background: #fee2e2; color: #991b1b; }
.date { color: #6b7280; }
.verified-badge { background: #10b981; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
.review-content { margin-bottom: 12px; }
.comment { color: #4b5563; margin-bottom: 8px; line-height: 1.6; }
.review-images { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.review-image { width: 80px; height: 80px; object-fit: cover; border-radius: 6px; border: 1px solid #e5e7eb; }
.review-actions { display: flex; gap: 8px; }
.btn { padding: 6px 12px; border: 1px solid #d1d5db; border-radius: 6px; background: white; cursor: pointer; font-size: 14px; }
.btn.outline { border-color: #2563eb; color: #2563eb; }
.btn.outline:hover { background: #2563eb; color: white; }
.btn.danger { border-color: #ef4444; color: #ef4444; }
.btn.danger:hover { background: #ef4444; color: white; }
.pagination { display: flex; gap: 12px; align-items: center; justify-content: center; margin-top: 24px; }
.pagination button { padding: 6px 12px; border: 1px solid #d1d5db; border-radius: 6px; background: white; cursor: pointer; }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
