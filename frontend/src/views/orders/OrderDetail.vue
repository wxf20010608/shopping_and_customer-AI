<template>
  <section v-if="order" class="detail">
    <header class="detail-header">
      <h2>订单详情 #{{ order.id }}</h2>
      <span class="status">{{ statusLabel(order.status) }}</span>
    </header>
    <div class="meta">
      <p>支付方式：{{ payLabel(order.payment_method) }}</p>
      <p>合计金额：￥{{ order.total_amount.toFixed(2) }}</p>
      <p>收货地址：{{ order.shipping_address }}</p>
      <p>下单时间：{{ formatDate(order.created_at) }}</p>
    </div>
    <div class="discount" v-if="order">
      <h3>优惠说明</h3>
      <p>原始金额：￥{{ originalTotal.toFixed(2) }}</p>
      <p v-if="order.discount_amount > 0">优惠减免：￥{{ order.discount_amount.toFixed(2) }}</p>
      <p v-else>无优惠</p>
      <p v-if="order.discount_type==='coupon'">使用优惠券：{{ couponInfo?.coupon?.code || '（编码未知）' }}</p>
      <p v-if="order.discount_type==='membership'">会员折扣购买{{ membershipPlanLabel }}</p>
    </div>
    <h3>商品清单</h3>
    <ul class="items">
      <li v-for="item in order.items" :key="item.id">
        <div>
          <strong>{{ item.product.name }}</strong>
          <p>数量：{{ item.quantity }}</p>
          <p v-if="order.status === 'completed' && !item.reviewed" class="review-prompt">
            <router-link :to="{ name: 'product-detail', params: { id: item.product.id } }" class="review-link">
              💬 去评价此商品
            </router-link>
          </p>
        </div>
        <span class="price">￥{{ item.unit_price.toFixed(2) }}</span>
      </li>
    </ul>
    <div class="actions">
      <router-link class="btn secondary" :to="firstChatLink">联系客服</router-link>
      <router-link v-if="order.status === 'completed'" class="btn" to="/profile/reviews">查看我的评价</router-link>
    </div>
  </section>
  <div v-else class="loading">加载中...</div>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import { useRoute } from "vue-router";
import { api } from "../../api";
import { useUserStore } from "../../stores/user";

const route = useRoute();
const userStore = useUserStore();
const order = ref(null);
const userCoupons = ref([]);
const membership = ref(null);
const membershipPlans = ref([]);
const couponInfo = ref(null);
const firstProductId = computed(() => order.value?.items?.[0]?.product?.id || null);
const firstChatLink = computed(() => ({ name: 'chat', params: { productId: firstProductId.value || undefined } }));

const originalTotal = computed(() => {
  if (!order.value) return 0;
  return (order.value.items || []).reduce((sum, it) => sum + it.unit_price * it.quantity, 0);
});

const membershipPlanLabel = computed(() => {
  if (!membership.value) return "（需开通会员）";
  const planId = membership.value.plan_id;
  if (!planId) return "（无折扣计划）";
  const plan = membershipPlans.value.find(p => p.id === planId);
  if (!plan) return "（计划信息不可用）";
  return `（${plan.name}，折扣${plan.discount_percent}%）`;
});

const statusMap = { pending: "待支付", paid: "已支付", shipped: "已发货", completed: "已完成", cancelled: "已取消" };
const paymentMap = { alipay: "支付宝", wechat: "微信支付", bank_card: "银行卡", cod: "货到付款" };

function statusLabel(status){ return statusMap[status] || status; }
function payLabel(m){ return paymentMap[m] || m; }
function formatDate(d){ try { if(!d) return '-'; return new Date(d).toLocaleString() } catch { return String(d)||'-' } }

async function loadOrder(){
  const id = Number(route.params.id);
  const { data } = await api.getOrderDetail(id);
  order.value = data;
  await Promise.allSettled([
    loadUserCoupons(),
    loadMembership(),
    loadMembershipPlans(),
  ]);
  if (order.value?.discount_type === 'coupon') {
    couponInfo.value = (userCoupons.value || []).find(uc => uc.used_order_id === order.value.id) || null;
  }
}

async function loadUserCoupons(){
  try { const { data } = await api.listUserCoupons(userStore.userId); userCoupons.value = data || []; } catch {}
}
async function loadMembership(){
  try { const { data } = await api.getMembership(userStore.userId); membership.value = data; } catch { membership.value = null }
}
async function loadMembershipPlans(){
  try { const { data } = await api.listMembershipPlans(); membershipPlans.value = data || []; } catch {}
}

onMounted(() => { loadOrder(); });
</script>

<style scoped>
.detail { background: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); padding: 16px; }
.detail-header { display: flex; justify-content: space-between; align-items: baseline; }
.status { color: #2563eb; font-weight: 600; }
.meta { color: #374151; }
.items { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.items li { display: flex; justify-content: space-between; align-items: center; }
.price { font-weight: 600; }
.review-prompt { margin-top: 8px; }
.review-link { color: #2563eb; text-decoration: none; font-size: 14px; }
.review-link:hover { text-decoration: underline; }
.discount { margin-top: 16px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; }
.loading { padding: 32px; text-align: center; }
</style>