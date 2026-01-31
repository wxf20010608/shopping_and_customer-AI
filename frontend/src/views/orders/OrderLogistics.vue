<template>
  <section v-if="shipping" class="detail">
    <header class="detail-header">
      <h2>物流信息 #{{ orderId }}</h2>
      <span class="status">{{ shippingLabel(shipping.status) }}</span>
    </header>
    <div class="meta">
      <p>物流公司：{{ shipping.carrier }}</p>
      <p v-if="shipping.tracking_number">运单号：{{ shipping.tracking_number }}</p>
      <p v-if="shipping.estimated_delivery">预计送达：{{ formatDate(shipping.estimated_delivery) }}</p>
    </div>
    <button class="btn outline" @click="refresh">刷新</button>
  </section>
  <div v-else class="loading">加载中...</div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { api } from "../../api";

const route = useRoute();
const orderId = Number(route.params.id);
const shipping = ref(null);

const shippingMap = { created: "待揽收", in_transit: "运输中", delivered: "已签收", returned: "已退回" };
function shippingLabel(s){ return shippingMap[s] || s; }
function formatDate(d){ try { if(!d) return '-'; return new Date(d).toLocaleString() } catch { return String(d)||'-' } }

async function load(){
  const { data } = await api.getLogistics(orderId);
  shipping.value = data;
}
async function refresh(){ await load() }

onMounted(() => { load() })
</script>

<style scoped>
.detail { background: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); padding: 16px; }
.detail-header { display: flex; justify-content: space-between; align-items: baseline; }
.status { color: #2563eb; font-weight: 600; }
.meta { color: #374151; }
.loading { padding: 32px; text-align: center; }
.btn { height: 36px; padding: 0 12px; border: none; border-radius: 6px; background: #1d4ed8; color: #fff; cursor: pointer; }
.btn.outline { background:#fff; border:1px solid #1d4ed8; color:#1d4ed8; }
</style>