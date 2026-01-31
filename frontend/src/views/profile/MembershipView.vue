<template>
  <div class="membership">
    <h2>会员中心</h2>
    <div class="card">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else>
        <div v-if="membership" class="current">
          <div class="current-card">
            <div class="cover" :style="{ backgroundImage: gradientByLevel(membership.level) }"></div>
            <div class="info">
              <h3>当前会员：{{ levelLabel(membership.level) }}</h3>
              <p>状态：{{ membership.status }}</p>
              <p>余额：￥{{ membership.balance.toFixed(2) }}</p>
              <p v-if="membership.plan_id">计划：{{ plans.find(p=>p.id===membership.plan_id)?.name || ('#'+membership.plan_id) }}</p>
            </div>
          </div>
        </div>
        <h3>会员等级</h3>
        <div class="level-grid">
          <article v-for="lv in levels" :key="lv.key" class="level-card">
            <img class="cover" :src="levelImage(lv.key)" alt="" />
            <div class="level-info">
              <h3>{{ lv.name }}</h3>
              <p class="desc">专属权益与折扣，立即开通体验。</p>
              <div class="actions">
                <button class="btn outline" @click="viewLevel(lv)">查看详情</button>
                <button class="btn" :disabled="!!membership?.plan_id || !hasPublishedForLevel(lv.key)" @click="buyLevel(lv)">购买会员</button>
              </div>
            </div>
          </article>
        </div>
        <h3>会员类型</h3>
        <div class="plan-grid">
          <article v-for="p in plans" :key="p.id" class="plan-card">
            <img class="cover" :src="cardImage(p)" alt="" />
            <header class="plan-header">
              <h3>{{ p.name }}</h3>
              <span class="badge" v-if="p.active">在售</span>
              <span class="badge inactive" v-else>停售</span>
            </header>
            <p class="desc">编码：{{ p.code }}</p>
            <p class="desc">折扣：{{ (100 - p.discount_percent) }}% 折扣</p>
            <div class="actions">
              <button class="btn outline" @click="viewPlan(p)">查看详情</button>
              <button class="btn" :disabled="!p.active || !!membership?.plan_id" @click="buy(p)">购买会员</button>
            </div>
          </article>
        </div>
        <div v-if="activePlan" class="plan-detail">
          <div class="detail-inner">
            <img class="cover" :src="cardImage(activePlan)" alt="" />
            <div class="meta">
              <h3>{{ activePlan.name }}</h3>
              <p>编码：{{ activePlan.code }}</p>
              <p>折扣说明：消费金额按照 {{ (100 - activePlan.discount_percent) }}% 折扣计算</p>
              <p>状态：{{ activePlan.active ? '在售' : '停售' }}</p>
              <div class="actions">
                <button class="btn outline" @click="activePlan=null">关闭</button>
                <button class="btn" :disabled="!activePlan.active || membership?.plan_id===activePlan.id || !hasPublishedForPlanId(activePlan.id)" @click="buy(activePlan)">立即购买</button>
              </div>
            </div>
          </div>
        </div>
        <div v-if="activeLevel" class="plan-detail">
          <div class="detail-inner">
            <div class="cover" :style="{ backgroundImage: gradientByLevel(activeLevel.key) }"></div>
            <div class="meta">
              <h3>{{ activeLevel.name }}</h3>
              <p>权益：更高折扣与专属服务。</p>
              <div class="actions">
                <button class="btn outline" @click="activeLevel=null">关闭</button>
                <button class="btn" :disabled="membership?.level===activeLevel.key" @click="buyLevel(activeLevel)">立即购买</button>
              </div>
            </div>
          </div>
        </div>
        <div v-if="cards.length" class="my-cards">
          <h3>我的会员卡</h3>
          <div class="plan-grid">
            <article v-for="c in cards" :key="c.id" class="plan-card">
              <div class="cover" :style="{ backgroundImage: gradientByLevel(plans.find(p=>p.id===c.plan_id)?.code || 'card') }"></div>
              <header class="plan-header">
                <h3>卡号：{{ c.card_no }}</h3>
                <span class="badge" :class="{ inactive: c.status!=='assigned' }">{{ c.status }}</span>
              </header>
              <p class="desc">计划：{{ (plans.find(p=>p.id===c.plan_id)?.name) || ('#'+c.plan_id) }}</p>
              <p class="desc">余额：￥{{ c.balance.toFixed(2) }}</p>
            </article>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { api } from '@/api'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(true)
const membership = ref(null)
const plans = ref([])
const cards = ref([])
const publishedCards = ref([])
const createForm = ref({ level: 'standard', plan_id: null, extra_info: '' })
const editForm = ref({ level: 'standard', plan_id: null, status: 'active', extra_info: '' })
const rechargeAmount = ref(100)
const activePlan = ref(null)
const activeLevel = ref(null)
const levels = [
  { key: 'premium', name: '高级会员' },
  { key: 'plus', name: '中级会员' },
  { key: 'standard', name: '普通会员' },
]
const plansLoaded = computed(() => Array.isArray(plans.value) && plans.value.length > 0)

function levelLabel(level){ return level === 'premium' ? '高级会员' : '标准会员' }
function cardImage(p){ const seed = `${p.code || 'plan'}-${p.id}`; return `https://picsum.photos/seed/${encodeURIComponent(seed)}/360/200` }
function gradientByLevel(seed){ const a = Math.abs(String(seed).split('').reduce((s,c)=>s + c.charCodeAt(0),0)%360); const b = (a+60)%360; return `linear-gradient(135deg, hsl(${a},70%,60%), hsl(${b},70%,60%))` }
function levelImage(lv){ const seed = `level-${lv}`; return `https://picsum.photos/seed/${encodeURIComponent(seed)}/360/200` }
function findPlanByLevel(level){
  const list = (plans.value || []).filter(p => p && p.active)
  if (!list.length) {
    return (plans.value || [])[0]
  }
  const sorted = [...list].sort((a,b) => (a.discount_percent||0) - (b.discount_percent||0))
  if (level === 'premium') return sorted[sorted.length - 1]
  if (level === 'plus') return sorted[Math.floor(sorted.length / 2)]
  return sorted[0]
}
function hasPublishedForPlanId(planId){
  return (publishedCards.value || []).some(c => c.plan_id === planId)
}
function hasPublishedForLevel(level){
  const p = findPlanByLevel(level)
  return p ? hasPublishedForPlanId(p.id) : false
}
function viewLevel(l){
  router.push({ name: 'membership-detail-level', params: { level: l.key } })
}
function buyLevel(l){
  const p = findPlanByLevel(l.key)
  if (!p || !hasPublishedForPlanId(p.id)){
    alert('暂无发布的会员卡，暂不可购买')
    return
  }
  router.push({ name: 'membership-purchase-level', params: { level: l.key } })
}

async function load(){
  try {
    const { data } = await api.getMembership(userStore.userId)
    membership.value = data
    editForm.value = { level: data.level, plan_id: data.plan_id || null, status: data.status, extra_info: data.extra_info || '' }
  } catch (e) {
    membership.value = null
  } finally { loading.value = false }
}

async function loadPlans(){
  try { const { data } = await api.listMembershipPlans(); plans.value = data } catch{}
}

async function loadCards(){
  try { const { data } = await api.listMyMembershipCards(userStore.userId); cards.value = data } catch{}
}
async function loadPublishedCards(){
  try { const { data } = await api.listPublishedMembershipCards(); publishedCards.value = data } catch{}
}

async function create(){
  try { const { data } = await api.createMembership(userStore.userId, createForm.value); membership.value = data; await load() } catch(err){ alert(err?.response?.data?.detail || '开通失败') }
}

function viewPlan(p){
  router.push({ name: 'membership-detail', params: { id: p.id } })
}

async function buy(p){
  if (!p?.id) return
  if (!hasPublishedForPlanId(p.id)){
    alert('暂无发布的会员卡，暂不可购买')
    return
  }
  router.push({ name: 'membership-purchase', params: { id: p.id } })
}

async function save(){
  try { const { data } = await api.updateMembership(userStore.userId, editForm.value); membership.value = data } catch(err){ alert(err?.response?.data?.detail || '保存失败') }
}

async function recharge(){
  try { const { data } = await api.rechargeMembership(userStore.userId, rechargeAmount.value); membership.value = data } catch(err){ alert(err?.response?.data?.detail || '充值失败') }
}

onMounted(async () => {
  const id = userStore.userId
  if (!id) return router.replace('/login')
  await Promise.all([load(), loadPlans(), loadCards(), loadPublishedCards()])
})
</script>

<style scoped>
.membership { max-width: 960px; margin: 24px auto; }
.card { padding: 18px; border: 1px solid #eee; border-radius: 12px; background: #fff; }
.loading { color: #666; }
.current-card { display: grid; grid-template-columns: 360px 1fr; gap: 16px; align-items: center; margin-bottom: 16px; }
.cover { width: 100%; height: 200px; border-radius: 12px; object-fit: cover; background-size: cover; background-position: center; }
.level-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 12px; }
.level-card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 12px; background: #fff; display: grid; gap: 10px; }
.level-info h3 { margin: 4px 0; }
.level-info .actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.plan-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 12px; }
.plan-card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 12px; background: #fff; display: grid; gap: 10px; }
.plan-header { display: flex; justify-content: space-between; align-items: center; }
.badge { background: #10b981; color: #fff; border-radius: 6px; padding: 2px 8px; font-size: 12px; }
.badge.inactive { background: #6b7280; }
.desc { color: #4b5563; margin: 6px 0; }
.actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.btn { height: 36px; padding: 0 12px; border: none; border-radius: 6px; background: #1d4ed8; color: #fff; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
.btn.outline { background: #fff; border: 1px solid #1d4ed8; color: #1d4ed8; }
.plan-detail { margin-top: 16px; padding: 12px; border: 1px dashed #d1d5db; border-radius: 12px; background: #f9fafb; }
.detail-inner { display: grid; grid-template-columns: 360px 1fr; gap: 16px; align-items: start; }
.my-cards { margin-top: 16px; }
</style>