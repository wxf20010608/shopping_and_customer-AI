<template>
  <section>
    <h2>购物车</h2>
    <div v-if="!cartItems.length" class="empty">购物车为空，快去选购商品吧！</div>
    <div v-else class="cart-list">
      <div v-for="item in cartItems" :key="item.id" class="cart-item">
        <div class="info">
          <h3>{{ item.product.name }}</h3>
          <p>单价：￥{{ item.product.price.toFixed(2) }}</p>
          <p>库存：{{ item.product.stock }}</p>
        </div>
        <div class="controls">
          <input type="number" min="1" :max="item.product.stock" v-model.number="item.quantity" @change="updateQuantity(item)" />
          <button class="btn danger" @click="removeItem(item.id)">移除</button>
        </div>
      </div>
      <div class="summary">
        <p>商品总数：{{ cartItems.length }}</p>
        <p>合计金额：￥{{ totalPrice.toFixed(2) }}</p>
        <div class="discount">
          <label>
            优惠方式
            <div class="modes">
              <label><input type="radio" value="normal" v-model="buyMode" /> 原价</label>
              <label><input type="radio" value="membership" v-model="buyMode" :disabled="!membershipEligible" /> 会员购买</label>
              <label><input type="radio" value="coupon" v-model="buyMode" /> 使用优惠券</label>
            </div>
          </label>
          <div v-if="buyMode==='coupon'" class="coupon-select">
            <select v-model="selectedCouponId">
              <option :value="null">选择优惠券</option>
              <option v-for="uc in userCoupons" :key="uc.id" :value="uc.id">
                {{ uc.coupon.code }}（{{ uc.coupon.discount_type==='amount' ? '减￥'+uc.coupon.discount_value : (uc.coupon.discount_value+'%折扣') }}）
              </option>
            </select>
          </div>
          <p v-if="buyMode!=='normal'">预计支付：￥{{ payablePrice.toFixed(2) }}</p>
          <p v-if="!membershipEligible" class="hint">会员支付需先在会员中心开通并充值，<router-link to="/profile/membership">去开通</router-link></p>
        </div>
      </div>
      <div class="checkout">
        <h3>填写订单信息</h3>
        <label>
          收货地址
          <select v-model="selectedAddressId" @change="onAddressChange">
            <option v-for="addr in addresses" :key="addr.id" :value="addr.id">
              {{ formatAddress(addr) }}{{ addr.is_default ? ' (默认)' : '' }}
            </option>
          </select>
        </label>
        <label>物流公司
          <select v-model="orderForm.carrier">
            <option v-for="c in carriers" :key="c" :value="c">{{ c }}</option>
          </select>
        </label>
        <label>支付方式
          <select v-model="orderForm.payment">
            <option value="alipay">支付宝</option>
            <option value="wechat">微信支付</option>
            <option value="bank_card">银行卡</option>
            <option value="cod">货到付款</option>
          </select>
        </label>
        <button class="btn" :disabled="submitting" @click="submitOrder">{{ submitting ? "提交中..." : "提交订单" }}</button>
        <button class="btn outline" @click="clearCart">清空购物车</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { api } from "../../api";
import { useUserStore } from "../../stores/user";

const userStore = useUserStore();
const cartItems = ref([]);
const submitting = ref(false);
const addresses = ref([]);
const carriers = ["顺丰速运","京东物流","中通快递","圆通速递","韵达快递","申通快递","德邦物流"];
const orderForm = ref({ address: "", carrier: "顺丰速运", payment: "alipay" });
const selectedAddressId = ref(null);
const buyMode = ref('normal')
const userCoupons = ref([])
const selectedCouponId = ref(null)
const membership = ref(null)
const membershipPlans = ref([])

function onAddressChange() {
  const addr = addresses.value.find(a => a.id === selectedAddressId.value);
  if (addr) {
    orderForm.value.address = formatAddress(addr);
  } else {
    orderForm.value.address = "";
  }
}

const totalPrice = computed(() => cartItems.value.reduce((total, item) => total + item.product.price * item.quantity, 0))
const payablePrice = computed(() => {
  const base = totalPrice.value
  if (buyMode.value === 'membership') {
    const percent = membership.value?.plan_id ? (plansPercent[membership.value.plan_id] ?? 10) : 10
    return +(base * (1 - percent/100)).toFixed(2)
  }
  if (buyMode.value === 'coupon'){
    const uc = userCoupons.value.find(x => x.id === selectedCouponId.value)
    if (!uc) return base
    const v = uc.coupon.discount_value
    if (uc.coupon.discount_type === 'amount') return Math.max(0, +(base - v).toFixed(2))
    return +(base * (1 - v/100)).toFixed(2)
  }
  return base
})

const plansPercent = {}
const membershipEligible = computed(() => { const m = membership.value; if (!m) return false; return m.status === 'active' && (m.balance || 0) > 0 })

async function loadCart() { const { data } = await api.getCart(userStore.userId); cartItems.value = data.items }
function formatAddress(a){ return `${a.province || ''}${a.city || ''}${a.district || ''}${a.detail || ''}`.trim() }
async function loadAddresses(){ 
  const { data } = await api.listAddresses(userStore.userId); 
  addresses.value = data || []; 
  const def = addresses.value.find(a=>a.is_default) || addresses.value[0]; 
  if (def) {
    selectedAddressId.value = def.id;
    orderForm.value.address = formatAddress(def);
  } else {
    selectedAddressId.value = null;
    orderForm.value.address = "";
  }
}
async function loadCoupons(){ try { const { data } = await api.listUserCoupons(userStore.userId); userCoupons.value = data || [] } catch {} }
async function loadMembership(){ try { const { data } = await api.getMembership(userStore.userId); membership.value = data } catch { membership.value = null } }
async function loadMembershipPlans(){ try { const { data } = await api.listMembershipPlans(); membershipPlans.value = data; data.forEach(p => plansPercent[p.id] = p.discount_percent) } catch{} }

async function updateQuantity(item) { await api.updateCartItem(userStore.userId, item.id, { product_id: item.product.id, quantity: item.quantity }); await loadCart() }
async function removeItem(itemId) { await api.removeCartItem(userStore.userId, itemId); await loadCart() }
async function clearCart() { await api.clearCart(userStore.userId); await loadCart() }

async function submitOrder() {
  try {
    submitting.value = true;
    const basePayload = { shipping_address: orderForm.value.address, payment_method: orderForm.value.payment, shipping_carrier: orderForm.value.carrier }
    let payload = basePayload
    if (buyMode.value === 'membership') payload = { ...basePayload, use_membership: true }
    else if (buyMode.value === 'coupon' && selectedCouponId.value) payload = { ...basePayload, coupon_id: selectedCouponId.value }
    const { data } = await api.createOrder(userStore.userId, payload)
    alert(`订单创建成功，订单号 #${data.id}`)
    await loadCart()
  } finally {
    submitting.value = false
  }
}

onMounted(async () => { await Promise.all([loadCart(), loadAddresses(), loadCoupons(), loadMembership(), loadMembershipPlans()]) })
</script>

<style scoped>
.empty { padding: 32px; text-align: center; }
.cart-list { display: flex; flex-direction: column; gap: 12px; }
.cart-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; border: 1px solid #eee; border-radius: 8px; }
.summary { padding: 12px; border: 1px solid #eee; border-radius: 8px; }
.discount .modes { display: flex; gap: 12px; }
.checkout { margin-top: 12px; display: grid; gap: 8px; }
.btn { padding: 6px 12px; border-radius: 6px; background: #1d4ed8; color: #fff; border: none; }
.btn.outline { background: #fff; border: 1px solid #1d4ed8; color: #1d4ed8; }
.btn.danger { background: #ef4444; }
label { display: grid; gap: 6px; }
label select { padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px; }
</style>