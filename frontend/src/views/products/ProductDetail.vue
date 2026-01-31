<template>
  <section v-if="product" class="detail">
    <header class="detail-header">
      <h2>{{ product.name }}</h2>
      <span class="price">￥{{ product.price.toFixed(2) }}</span>
    </header>
    <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="cover" />
    <div class="meta">
      <p>分类：{{ product.category || "未分类" }}</p>
      <p>库存：{{ product.stock }}</p>
      <p v-if="product.created_at">上架时间：{{ new Date(product.created_at).toLocaleString() }}</p>
      <div v-if="reviewStats" class="rating-info">
        <span class="rating">评分：{{ reviewStats.avg_rating.toFixed(1) }} ⭐</span>
        <span class="review-count">评价数：{{ reviewStats.total_reviews }}</span>
      </div>
    </div>
    <p class="desc">{{ product.description || "暂无简介" }}</p>
    <div class="actions">
      <label>
        购买数量
        <input type="number" min="1" :max="product.stock" v-model.number="quantity" />
      </label>
      <button class="btn" :disabled="adding" @click="addToCart">
        {{ adding ? "加入中..." : "加入购物车" }}
      </button>
      <button class="btn outline" @click="toggleWishlist">
        {{ wishlist.has(product) ? "取消收藏" : "收藏" }}
      </button>
      <router-link class="btn secondary" :to="{ name: 'chat', params: { productId: product.id } }">联系客服</router-link>
    </div>

    <!-- 商品评价区域 -->
    <div class="reviews-section">
      <h3>商品评价</h3>
      
      <!-- 评价统计 -->
      <div v-if="reviewStats" class="review-stats">
        <div class="stats-item">
          <strong>平均评分：</strong>{{ reviewStats.avg_rating.toFixed(1) }} ⭐
        </div>
        <div class="stats-item">
          <strong>总评价数：</strong>{{ reviewStats.total_reviews }}
        </div>
        <div class="stats-item" v-if="reviewStats.rating_distribution">
          <strong>评分分布：</strong>
          <span v-for="(count, rating) in reviewStats.rating_distribution" :key="rating" class="dist-item">
            {{ rating }}星: {{ count }}
          </span>
        </div>
      </div>

      <!-- 发表评价表单 -->
      <div v-if="userStore.userId" class="review-form">
        <h4>发表评价</h4>
        <div class="form-group">
          <label>评分：</label>
          <select v-model.number="reviewForm.rating" required>
            <option value="">请选择</option>
            <option :value="5">5星</option>
            <option :value="4">4星</option>
            <option :value="3">3星</option>
            <option :value="2">2星</option>
            <option :value="1">1星</option>
          </select>
        </div>
        <div class="form-group">
          <label>评价内容：</label>
          <textarea v-model="reviewForm.comment" placeholder="请输入您的评价..." rows="4"></textarea>
        </div>
        <button class="btn" @click="submitReview" :disabled="submitting">
          {{ submitting ? "提交中..." : "提交评价" }}
        </button>
      </div>
      <div v-else class="review-login-prompt">
        <p>请先<a @click="router.push('/login')">登录</a>后再发表评价</p>
      </div>

      <!-- 评价列表 -->
      <div class="reviews-list">
        <h4>评价列表（{{ reviewsPage.total }}条）</h4>
        <div v-if="reviewsPage.items && reviewsPage.items.length > 0">
          <div v-for="review in reviewsPage.items" :key="review.id" class="review-item">
            <div class="review-header">
              <span class="review-rating">⭐ {{ review.rating }}</span>
              <span class="review-user">{{ review.user?.username || '匿名用户' }}</span>
              <span v-if="review.verified_purchase" class="verified-badge">已购买</span>
              <span class="review-date">{{ new Date(review.created_at).toLocaleString() }}</span>
            </div>
            <div class="review-comment">{{ review.comment || '无评价内容' }}</div>
            <div v-if="review.images_list && review.images_list.length > 0" class="review-images">
              <img v-for="(img, idx) in review.images_list" :key="idx" :src="img" :alt="`评价图片${idx+1}`" class="review-image" />
            </div>
          </div>
        </div>
        <div v-else class="no-reviews">暂无评价</div>
        
        <!-- 分页 -->
        <div v-if="reviewsPage.total > reviewsPage.page_size" class="pagination">
          <button @click="loadReviews(reviewsPage.page - 1)" :disabled="reviewsPage.page <= 1">上一页</button>
          <span>第 {{ reviewsPage.page }} / {{ Math.ceil(reviewsPage.total / reviewsPage.page_size) }} 页</span>
          <button @click="loadReviews(reviewsPage.page + 1)" :disabled="reviewsPage.page >= Math.ceil(reviewsPage.total / reviewsPage.page_size)">下一页</button>
        </div>
      </div>
    </div>
  </section>
  <div v-else class="loading">加载中...</div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "../../api";
import { useUserStore } from "../../stores/user";
import { useWishlistStore } from "../../stores/wishlist";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const wishlist = useWishlistStore();
const product = ref(null);
const quantity = ref(1);
const adding = ref(false);

// 评价相关
const reviewStats = ref(null);
const reviewsPage = ref({ items: [], total: 0, page: 1, page_size: 10 });
const reviewForm = ref({ rating: null, comment: '', order_id: null });
const submitting = ref(false);

async function loadProduct() {
  const id = Number(route.params.id);
  const { data } = await api.getProduct(id);
  product.value = data;
  quantity.value = 1;
  // 加载评价统计和列表
  loadReviewStats();
  loadReviews();
}

async function loadReviewStats() {
  if (!product.value) return;
  try {
    const { data } = await api.getProductReviewStats(product.value.id);
    reviewStats.value = data;
  } catch (e) {
    console.warn("加载评价统计失败:", e);
  }
}

async function loadReviews(page = 1) {
  if (!product.value) return;
  try {
    const { data } = await api.getProductReviews(product.value.id, 'approved', page, 10);
    reviewsPage.value = data;
    // 解析图片JSON
    if (data.items) {
      data.items.forEach(item => {
        if (item.images) {
          try {
            item.images_list = JSON.parse(item.images);
          } catch {
            item.images_list = [];
          }
        } else {
          item.images_list = [];
        }
      });
    }
  } catch (e) {
    console.warn("加载评价列表失败:", e);
  }
}

async function submitReview() {
  if (!userStore.userId || !product.value) {
    alert("请先登录");
    router.push('/login');
    return;
  }
  
  if (!reviewForm.value.rating) {
    alert("请选择评分");
    return;
  }

  submitting.value = true;
  try {
    await api.createReview(product.value.id, userStore.userId, {
      rating: reviewForm.value.rating,
      comment: reviewForm.value.comment || null,
      order_id: reviewForm.value.order_id || null
    });
    alert("评价提交成功");
    // 重置表单
    reviewForm.value = { rating: null, comment: '', order_id: null };
    // 重新加载评价
    loadReviewStats();
    loadReviews(reviewsPage.value.page);
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || "评价提交失败");
  } finally {
    submitting.value = false;
  }
}

function toggleWishlist(){
  if (!userStore.userId){
    alert("请先登录后再加入心愿单");
    router.push('/login');
    return;
  }
  if (product.value){
    wishlist.toggle(product.value);
  }
}

async function addToCart() {
  if (!product.value) return;
  adding.value = true;
  try {
    await api.addToCart(userStore.userId, {
      product_id: product.value.id,
      quantity: quantity.value,
    });
    product.value.stock = Math.max(0, (product.value.stock || 0) - quantity.value);
    alert("已加入购物车");
  } finally {
    adding.value = false;
  }
}

onMounted(() => {
  loadProduct();
});
</script>

<style scoped>
.detail { background-color: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); padding: 16px; }
.detail-header { display: flex; justify-content: space-between; align-items: baseline; }
.cover { width: 100%; max-height: 360px; object-fit: cover; border-radius: 12px; margin: 12px 0; }
.price { color: #ef4444; font-weight: 600; }
.meta { color: #2563eb; }
.meta .rating-info { margin-top: 8px; display: flex; gap: 16px; }
.meta .rating { color: #f59e0b; font-weight: 600; }
.meta .review-count { color: #6b7280; }
.desc { color: #4b5563; margin: 12px 0; white-space: pre-line; }
.actions { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.actions input { width: 80px; padding: 4px; border: 1px solid #d1d5db; border-radius: 6px; }
.btn.secondary { background-color: #10b981; }
.btn.secondary:hover { background-color: #059669; }
.loading { padding: 32px; text-align: center; }

/* 评价区域样式 */
.reviews-section { margin-top: 24px; padding-top: 24px; border-top: 1px solid #e5e7eb; }
.reviews-section h3 { font-size: 20px; margin-bottom: 16px; }
.review-stats { background: #f9fafb; padding: 12px; border-radius: 8px; margin-bottom: 16px; }
.stats-item { margin: 8px 0; }
.stats-item .dist-item { margin-left: 12px; color: #6b7280; }
.review-form { background: #f9fafb; padding: 16px; border-radius: 8px; margin-bottom: 16px; }
.review-form h4 { margin-bottom: 12px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 4px; font-weight: 500; }
.form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; }
.form-group textarea { resize: vertical; }
.review-login-prompt { padding: 12px; background: #fef3c7; border-radius: 8px; text-align: center; }
.review-login-prompt a { color: #2563eb; cursor: pointer; text-decoration: underline; }
.reviews-list h4 { margin-bottom: 12px; }
.review-item { padding: 12px; border: 1px solid #e5e7eb; border-radius: 8px; margin-bottom: 12px; }
.review-header { display: flex; gap: 12px; align-items: center; margin-bottom: 8px; flex-wrap: wrap; }
.review-rating { color: #f59e0b; font-weight: 600; }
.review-user { color: #2563eb; }
.verified-badge { background: #10b981; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
.review-date { color: #6b7280; font-size: 14px; margin-left: auto; }
.review-comment { color: #4b5563; margin-bottom: 8px; }
.review-images { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.review-image { width: 100px; height: 100px; object-fit: cover; border-radius: 6px; border: 1px solid #e5e7eb; }
.no-reviews { padding: 24px; text-align: center; color: #6b7280; }
.pagination { display: flex; gap: 12px; align-items: center; justify-content: center; margin-top: 16px; }
.pagination button { padding: 6px 12px; border: 1px solid #d1d5db; border-radius: 6px; background: white; cursor: pointer; }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
