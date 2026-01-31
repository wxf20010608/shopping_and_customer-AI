<template>
  <section>
    <h2>我的订单</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="!orders.length" class="empty">暂无订单</div>
    <div v-else class="order-list">
      <article v-for="order in orders" :key="order.id" class="order-card">
        <header class="order-header">
          <span>订单号：{{ order.id }}</span>
          <span class="status">状态：{{ statusLabel(order.status) }}</span>
        </header>
        <ul class="order-items">
          <li v-for="item in order.items" :key="item.id">
            <div>
              <strong>{{ item.product.name }}</strong>
              <p>数量：{{ item.quantity }}</p>
            </div>
            <div class="price">￥{{ item.unit_price.toFixed(2) }}</div>
          </li>
        </ul>
        <footer class="order-footer">
          <div class="order-info">
            <p>支付方式：{{ payLabel(order.payment_method) }}</p>
            <p>合计：￥{{ order.total_amount.toFixed(2) }}</p>
            <p>收货地址：{{ order.shipping_address }}</p>
            <p>下单时间：{{ formatDate(order.created_at) }}</p>
          </div>
          <div class="right-col">
            <div v-if="logistics[order.id]" class="shipping">
              <p>物流公司：{{ logistics[order.id].carrier }}</p>
              <p>物流状态：{{ shippingLabel(logistics[order.id].status) }}</p>
              <p v-if="logistics[order.id].tracking_number">运单号：{{ logistics[order.id].tracking_number }}</p>
              <p v-if="logistics[order.id].estimated_delivery">预计送达：{{ formatDate(logistics[order.id].estimated_delivery) }}</p>
            </div>
            <div class="btns">
              <RouterLink class="btn outline" :to="{ name: 'order-detail', params: { id: order.id } }">查看详情</RouterLink>
              <RouterLink class="btn outline" :to="{ name: 'order-logistics', params: { id: order.id } }">查看物流</RouterLink>
              <button class="btn danger" @click="removeOrder(order)">删除订单</button>
            </div>
          </div>
        </footer>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref, reactive } from "vue";
import { api } from "../../api";
import { useUserStore } from "../../stores/user";

const userStore = useUserStore();
const orders = ref([]);
const loading = ref(false);
const logistics = reactive({});

const statusMap = { pending: "待支付", paid: "已支付", shipped: "已发货", completed: "已完成", cancelled: "已取消" };
const paymentMap = { alipay: "支付宝", wechat: "微信支付", bank_card: "银行卡", cod: "货到付款" };
const shippingMap = { created: "待揽收", in_transit: "运输中", delivered: "已签收", returned: "已退回" };

function statusLabel(status) { return statusMap[status] || status; }
function payLabel(method) { return paymentMap[method] || method; }
function shippingLabel(status) { return shippingMap[status] || status; }
function formatDate(dateString) { try { if (!dateString) return '-'; return new Date(dateString).toLocaleString() } catch { return String(dateString) || '-' } }

async function loadOrders() {
  loading.value = true;
  try {
    const { data } = await api.getOrders(userStore.userId);
    orders.value = data;
  } finally { loading.value = false; }
}

async function toggleLogistics(orderId) {
  if (logistics[orderId]) { delete logistics[orderId]; return; }
  const { data } = await api.getLogistics(orderId);
  logistics[orderId] = data;
}

async function removeOrder(order){
  if (!confirm(`确认删除订单 #${order.id}？`)) return
  try {
    await api.deleteOrder(userStore.userId, order.id)
    orders.value = orders.value.filter(o => o.id !== order.id)
    alert('已删除')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '删除失败')
  }
}

onMounted(() => { loadOrders(); });
</script>

<style scoped>
h2 { margin-bottom: 16px; }
.loading,.empty { padding: 32px; text-align: center; background-color: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08); }
.order-list { display: flex; flex-direction: column; gap: 16px; }
.order-card { background-color: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08); padding: 16px; display: flex; flex-direction: column; gap: 16px; }
.order-header { display: flex; justify-content: space-between; font-weight: 600; }
.status { color: #2563eb; }
.order-items { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.order-items li { display: flex; justify-content: space-between; align-items: center; }
.price { font-weight: 600; }
.order-footer { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
.order-info { flex: 1; }
.order-info p { margin: 4px 0; color: #6b7280; font-size: 14px; }
.right-col { display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
.shipping { text-align: right; font-size: 13px; color: #6b7280; }
.shipping p { margin: 2px 0; }
.btns { 
  display: flex; 
  gap: 8px; 
  flex-wrap: wrap;
  justify-content: flex-end;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  white-space: nowrap;
  border: none;
}
.btn.outline {
  background: #fff;
  border: 1px solid #2563eb;
  color: #2563eb;
}
.btn.outline:hover {
  background: #2563eb;
  color: #fff;
}
.btn.danger {
  background: #fff;
  border: 1px solid #ef4444;
  color: #ef4444;
}
.btn.danger:hover {
  background: #ef4444;
  color: #fff;
}
</style>