<template>
  <section>
    <h2>心愿单</h2>
    <div v-if="!products.length" class="empty">暂无收藏的商品</div>
    <div v-else class="product-grid">
      <article v-for="p in products" :key="p.id" class="product-card">
        <h3>{{ p.name }}</h3>
        <p class="price">￥{{ p.price.toFixed(2) }}</p>
        <p class="desc">{{ p.description || "暂无简介" }}</p>
        <div class="actions">
          <RouterLink class="btn outline" :to="{ name: 'product-detail', params: { id: p.id } }">查看详情</RouterLink>
          <button class="btn danger" @click="remove(p.id)">移除收藏</button>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { api } from "../../api";
import { useWishlistStore } from "../../stores/wishlist";

const wishlist = useWishlistStore();
const products = ref([]);

async function load(){
  const ids = wishlist.items;
  const results = [];
  for (const id of ids){
    const { data } = await api.getProduct(id);
    results.push(data);
  }
  products.value = results;
}

function remove(id){
  wishlist.toggle(id);
  load();
}

onMounted(() => load());
</script>

<style scoped>
h2 { margin-bottom: 16px; }
.empty { padding: 32px; text-align: center; background: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.product-grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
.product-card { background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; flex-direction: column; gap: 8px; }
.price { font-weight: 600; color: #ef4444; }
.desc { color: #4b5563; }
.actions { display: flex; gap: 12px; }
.btn.outline { background: #fff; color: #2563eb; border: 1px solid #2563eb; }
.btn.danger { background-color: #ef4444; }
.btn.danger:hover { background-color: #dc2626; }
</style>