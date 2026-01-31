<template>
  <section class="layout">
    <aside class="sidebar">
      <h3>商品分类</h3>
      <ul class="category-list">
        <li :class="{ active: !activeCategory }" @click="selectCategory(null)">全部</li>
        <li v-for="c in categories" :key="c" :class="{ active: activeCategory === c }" @click="selectCategory(c)">{{ c }}</li>
      </ul>
    </aside>
    <div class="content">
      <div class="search-bar">
        <input v-model="keyword" placeholder="搜索商品名称或分类" @keyup.enter="fetchProducts" />
        <button class="btn" @click="fetchProducts">搜索</button>
      </div>
      <div class="product-grid">
        <article v-for="product in products" :key="product.id" class="product-card">
          <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="cover" />
          <h3>{{ product.name }}</h3>
          <p class="price">￥{{ product.price.toFixed(2) }}</p>
          <p class="desc">{{ product.description || "暂无简介" }}</p>
          <p class="stock">库存：{{ product.stock }}</p>
          <div class="actions">
            <label>
              购买数量
              <input type="number" min="1" :max="product.stock" v-model.number="quantities[product.id]" />
            </label>
            <button class="btn" :disabled="loadingProductId === product.id" @click="handleAddToCart(product.id)">
              {{ loadingProductId === product.id ? "加入中..." : "加入购物车" }}
            </button>
          </div>
          <router-link class="btn secondary" :to="{ name: 'chat', params: { productId: product.id } }">联系客服</router-link>
          <button class="btn outline" @click="handleWishlist(product)">
            {{ wishlist.has(product) ? "取消收藏" : "收藏" }}
          </button>
          <router-link class="btn outline" :to="`/product/${product.id}`">查看详情</router-link>
        </article>
      </div>
      <div class="pagination">
        <button class="btn" :disabled="page <= 1" @click="prevPage">上一页</button>
        <span>第 {{ page }} / {{ totalPages }} 页，共 {{ total }} 条</span>
        <button class="btn" :disabled="page >= totalPages" @click="nextPage">下一页</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from "vue";
import { api } from "../../api";
import { useUserStore } from "../../stores/user";
import { useWishlistStore } from "../../stores/wishlist";
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const wishlist = useWishlistStore();
const router = useRouter();
const products = ref([]);
const categories = ref([]);
const activeCategory = ref(null);
const keyword = ref("");
const loadingProductId = ref(null);
const quantities = reactive({});
const customerService = reactive({});
const page = ref(1);
const pageSize = ref(6);
const total = ref(0);
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));

async function fetchProducts() {
  const { data } = await api.getProducts(keyword.value || undefined, activeCategory.value || undefined, page.value, pageSize.value);
  products.value = data.items || [];
  total.value = data.total || 0;
  data.items?.forEach((item) => {
    if (!quantities[item.id]) quantities[item.id] = 1;
  });
}

async function fetchCategories(){
  const { data } = await api.getCategories();
  categories.value = data;
}

function selectCategory(c){
  activeCategory.value = c;
  page.value = 1;
  fetchProducts();
}

function prevPage(){
  if (page.value > 1){
    page.value -= 1;
    fetchProducts();
  }
}
function nextPage(){
  if (page.value < totalPages.value){
    page.value += 1;
    fetchProducts();
  }
}

async function handleAddToCart(productId) {
  loadingProductId.value = productId;
  try {
    const qty = quantities[productId] || 1;
    await api.addToCart(userStore.userId, {
      product_id: productId,
      quantity: qty,
    });
    const idx = products.value.findIndex(p => p.id === productId)
    if (idx !== -1) {
      const current = products.value[idx].stock || 0
      products.value[idx].stock = Math.max(0, current - qty)
    }
    alert("已加入购物车");
  } catch (error) {
    console.error(error);
    alert("加入购物车失败，请稍后再试");
  } finally {
    loadingProductId.value = null;
  }
}

async function loadCustomerService(productId) {
  if (customerService[productId]) {
    delete customerService[productId];
    return;
  }
  const { data } = await api.getCustomerService(productId);
  customerService[productId] = data.channels;
}

function handleWishlist(p){
  if (!userStore.userId){
    alert("请先登录后再加入心愿单");
    router.push('/login');
    return;
  }
  wishlist.toggle(p);
}

onMounted(() => {
  fetchCategories();
  fetchProducts();
});
</script>

<style scoped>
.layout { display: grid; grid-template-columns: 260px 1fr; gap: 16px; }
.sidebar { background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.sidebar h3 { margin-bottom: 12px; }
.category-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.category-list li { padding: 8px 12px; border-radius: 8px; cursor: pointer; }
.category-list li:hover { background: #f3f4f6; }
.category-list li.active { background: #1d4ed8; color: #fff; }
.search-bar { display: flex; gap: 12px; margin-bottom: 16px; }
.search-bar input { flex: 1; padding: 8px; border-radius: 6px; border: 1px solid #d1d5db; }
.product-grid { display: grid; gap: 16px; grid-template-columns: repeat(3, 1fr); }
.product-card { background-color: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; flex-direction: column; gap: 8px; }
.cover { width: 100%; height: 160px; object-fit: cover; border-radius: 8px; }
.price { font-size: 18px; font-weight: 600; color: #ef4444; }
.desc { flex: 1; color: #4b5563; }
.stock { color: #2563eb; }
.actions { display: flex; align-items: center; justify-content: flex-start; gap: 12px; flex-wrap: nowrap; }
.actions label { display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; flex-shrink: 0; }
.actions .btn { white-space: nowrap; flex-shrink: 0; min-width: 110px; }
.actions input { width: 80px; padding: 4px; border: 1px solid #d1d5db; border-radius: 6px; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 12px; padding: 16px 0; }
</style>