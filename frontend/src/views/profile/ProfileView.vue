<template>
  <div class="profile">
    <h2>个人中心</h2>
    <div v-if="user">
      <p><strong>用户名：</strong>{{ user.username }}</p>
      <p><strong>邮箱：</strong>{{ user.email }}</p>
      <p><strong>姓名：</strong>{{ user.full_name || '-' }}</p>
      <p><strong>电话：</strong>{{ user.phone || '-' }}</p>
      <p><strong>默认地址：</strong>{{ user.address || '-' }}</p>
      <div class="actions">
        <router-link class="btn" to="/profile/edit">编辑资料</router-link>
        <router-link class="btn" to="/profile/address">管理地址簿</router-link>
        <router-link class="btn" to="/profile/membership">会员中心</router-link>
        <button class="btn danger" @click="doLogout">退出登录</button>
        <button class="btn danger" @click="doDelete">注销账号</button>
      </div>
    </div>
    <div v-else>未登录，请先 <router-link to="/login">登录</router-link> 或 <router-link to="/register">注册</router-link></div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { api } from '@/api'

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.profile)

onMounted(async () => {
  const id = userStore.userId
  if (!id) return router.replace('/login')
  await userStore.refreshProfile()
})

function doLogout(){
  userStore.logout()
  router.replace('/login')
}

async function doDelete(){
  const id = userStore.userId
  if (!id) return router.replace('/login')
  if (!confirm('确认要注销并删除该账号吗？此操作不可恢复。')) return
  try {
    await api.deleteUser(id)
    alert('账号已删除')
    userStore.logout()
    router.replace('/login')
  } catch (e) {
    alert(e?.response?.data?.detail || '删除失败')
  }
}
</script>

<style scoped>
.profile { max-width: 720px; margin: 24px auto; padding: 24px; border: 1px solid #eee; border-radius: 8px; }
.actions { margin-top: 12px; display: flex; gap: 12px; }
.btn { display: inline-block; padding: 8px 14px; border-radius: 6px; background: #42b983; color: #fff; font-weight: 600; }
.btn.danger { background: #ef4444; }
</style>