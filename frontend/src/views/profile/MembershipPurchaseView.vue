<template>
  <div class="membership-purchase">
    <h2>购买会员</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="!plan" class="empty">暂无该级别在售计划，请联系管理员</div>
    <div v-else class="card">
      <header class="header">
        <h3>{{ plan.name }}</h3>
        <span class="badge" :class="{ inactive: !plan.active }">{{ plan.active ? '在售' : '停售' }}</span>
      </header>
      <p class="desc">编码：{{ plan.code }}，折扣：{{ (100 - plan.discount_percent) }}% 折扣</p>

      <div class="section">
        <h4>选择时长</h4>
        <div class="durations">
          <label v-for="opt in durationOptions" :key="opt.value" class="duration">
            <input type="radio" name="duration" :value="opt.value" v-model.number="duration" />
            <span>{{ opt.label }}</span>
            <strong>￥{{ priceFor(opt.value).toFixed(2) }}</strong>
          </label>
        </div>
      </div>

      <div class="section">
        <h4>支付方式</h4>
        <select v-model="payment">
          <option value="alipay">支付宝</option>
          <option value="wechat">微信支付</option>
          <option value="bank_card">银行卡</option>
        </select>
        <div v-if="payment==='bank_card'" class="bank">
          <input v-model="cardNo" placeholder="请输入银行卡号" />
          <p class="hint">仅用于绑定，系统不保存完整卡号</p>
        </div>
      </div>

      <div class="section" v-if="membership">
        <h4>当前会员</h4>
        <p>等级：{{ levelLabel(membership.level) }}；状态：{{ membership.status }}；余额：￥{{ (membership.balance||0).toFixed(2) }}</p>
        <p v-if="membership.plan_id" class="warn">已拥有会员计划，暂不支持重复购买</p>
      </div>

      <div class="actions">
        <router-link class="btn outline" to="/profile/membership">返回会员中心</router-link>
        <button class="btn" :disabled="!plan.active || submitting || !!membership?.plan_id || !hasPublishedForPlanId(plan.id)" @click="submit">确认支付 ￥{{ priceFor(duration).toFixed(2) }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(true)
const submitting = ref(false)
const plan = ref(null)
const membership = ref(null)
const publishedCards = ref([])
const payment = ref('alipay')
const cardNo = ref('')
const duration = ref(1)

const durationOptions = [
  { value: 1, label: '1个月' },
  { value: 2, label: '2个月' },
  { value: 12, label: '1年' },
]

function levelLabel(level){ return level==='premium' ? '高级会员' : (level==='plus' ? '中级会员' : '普通会员') }

function priceFor(months){
  const code = plan.value?.code || 'default'
  const base = code.includes('premium') ? 49 : (code.includes('plus') ? 29 : 19)
  if (months === 1) return base
  if (months === 2) return Math.round(base*1.85)
  if (months === 12) return base*10
  return base*months
}

function maskCard(no){ if(!no) return ''; const s = String(no).replace(/\s+/g,''); return s.length>4 ? `**** **** **** ${s.slice(-4)}` : s }

async function load(){
  try {
    const pc = api.listPublishedMembershipCards()
    const { data } = await api.listMembershipPlans()
    const id = route.params.id ? Number(route.params.id) : null
    const level = route.params.level || null
    if (id){
      plan.value = (data || []).find(p => p.id === id) || null
    } else if (level){
      const list = (data || []).filter(p => p && p.active)
      const match = (kw) => list.find(p => (p.code||'').toLowerCase().includes(kw) || (p.name||'').includes(kw))
      if (level === 'premium') plan.value = match('premium') || null
      else if (level === 'plus') plan.value = match('plus') || null
      else plan.value = match('standard') || null
      if (!plan.value) plan.value = list[0] || null
    }
    const { data: published } = await pc
    publishedCards.value = published
  } finally {
    loading.value = false
  }
}

async function loadMembership(){
  try { const { data } = await api.getMembership(userStore.userId); membership.value = data } catch { membership.value = null }
}

function inferLevel(code){ if(!code) return 'standard'; if(code.includes('premium')) return 'premium'; if(code.includes('plus')) return 'plus'; return 'standard' }

async function submit(){
  if (!plan.value) return
  if (!hasPublishedForPlanId(plan.value.id)) { alert('暂无发布的会员卡，暂不可购买'); return }
  try {
    submitting.value = true
    const info = `计划：${plan.value.name}；时长：${duration.value}个月；价格：￥${priceFor(duration.value).toFixed(2)}；支付：${payment.value}；卡：${maskCard(cardNo.value)}`
    if (!membership.value){
      const payload = { level: inferLevel(plan.value.code), plan_id: plan.value.id, extra_info: info }
      await api.createMembership(userStore.userId, payload)
    } else {
      if (membership.value.plan_id){
        alert('已拥有会员计划，不能重复购买')
        return
      }
      const payload = { level: membership.value.level, plan_id: plan.value.id, extra_info: info, status: membership.value.status }
      await api.updateMembership(userStore.userId, payload)
    }
    const amount = priceFor(duration.value)
    await api.rechargeMembership(userStore.userId, amount)
    alert(`购买成功，已充值 ￥${amount.toFixed(2)} 到会员余额`)
    router.replace('/cart')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || '购买失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const id = userStore.userId
  if (!id) return router.replace('/login')
  await Promise.all([load(), loadMembership()])
})
</script>

<style scoped>
.membership-purchase { max-width: 820px; margin: 24px auto; }
.card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; display: grid; gap: 12px; }
.header { display: flex; justify-content: space-between; align-items: baseline; }
.badge { background: #10b981; color: #fff; border-radius: 6px; padding: 2px 8px; font-size: 12px; }
.badge.inactive { background: #6b7280; }
.desc { color: #374151; }
.section { border-top: 1px dashed #e5e7eb; padding-top: 12px; }
.durations { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.duration { display: flex; align-items: center; justify-content: space-between; border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px 12px; }
.bank { display: grid; gap: 6px; margin-top: 8px; }
.hint { color: #6b7280; font-size: 12px; }
.warn { color: #ef4444; }
.actions { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.btn { background: #2563eb; color: #fff; border: none; border-radius: 8px; padding: 8px 16px; display: inline-flex; align-items: center; justify-content: center; }
.btn.outline { background: transparent; color: #2563eb; border: 1px solid #2563eb; }
.loading { color: #6b7280; }
.empty { color: #6b7280; }
</style>
function hasPublishedForPlanId(planId){ return (publishedCards.value || []).some(c => c.plan_id === planId) }