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

async function loadProduct() {
  const id = Number(route.params.id);
  const { data } = await api.getProduct(id);
  product.value = data;
  quantity.value = 1;
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
.desc { color: #4b5563; margin: 12px 0; white-space: pre-line; }
.actions { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.actions input { width: 80px; padding: 4px; border: 1px solid #d1d5db; border-radius: 6px; }
.btn.secondary { background-color: #10b981; }
.btn.secondary:hover { background-color: #059669; }
.loading { padding: 32px; text-align: center; }
</style>