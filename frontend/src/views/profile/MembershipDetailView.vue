<template>
  <div class="membership-detail">
    <h2>会员详情</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="!plan" class="empty">{{ emptyMessage }}</div>
    <div v-else class="card">
      <img class="cover" :src="cardImage(plan)" alt="" />
      <div class="info">
        <h3>{{ plan.name }}</h3>
        <p>编码：{{ plan.code }}</p>
        <p>折扣：{{ (100 - plan.discount_percent) }}% 折扣</p>
        <p>状态：{{ plan.active ? '在售' : '停售' }}</p>
      </div>
      <div class="actions">
        <router-link class="btn outline" to="/profile/membership">返回会员中心</router-link>
        <router-link class="btn" :class="{ disabled: !plan.active || !hasPublishedForPlanId(plan.id) }" :to="purchaseLink">立即购买</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'

const route = useRoute()
const loading = ref(true)
const plan = ref(null)
const emptyMessage = ref('计划不存在或已下架')
const publishedCards = ref([])

const purchaseLink = computed(() => {
  if (!plan.value) return { name: 'membership-purchase-level', params: { level: route.params.level || 'standard' } }
  return { name: 'membership-purchase', params: { id: plan.value.id } }
})

function cardImage(p){ const seed = `${p.code || 'plan'}-${p.id}`; return `https://picsum.photos/seed/${encodeURIComponent(seed)}/640/300` }
function hasPublishedForPlanId(planId){ return (publishedCards.value || []).some(c => c.plan_id === planId) }

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
      if (!plan.value) emptyMessage.value = '暂无该级别在售计划，请联系管理员'
    }
    const { data: published } = await pc
    publishedCards.value = published
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.membership-detail { max-width: 820px; margin: 24px auto; }
.card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; display: grid; gap: 12px; }
.cover { width: 100%; height: 300px; border-radius: 12px; object-fit: cover; }
.info { color: #374151; }
.actions { display: flex; gap: 12px; }
.btn { background: #2563eb; color: #fff; border: none; border-radius: 8px; padding: 8px 16px; }
.btn.outline { background: transparent; color: #2563eb; border: 1px solid #2563eb; }
.btn.disabled { opacity: .5; pointer-events: none; }
.loading { color: #6b7280; }
.empty { color: #6b7280; }
</style>