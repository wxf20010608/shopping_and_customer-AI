<template>
  <div class="auth-container">
    <h2>登录</h2>
    <form @submit.prevent="onSubmit">
      <div class="form-item">
        <label>用户名或邮箱</label>
        <input v-model="form.identity" placeholder="请输入用户名或邮箱" required />
      </div>
      <div class="form-item">
        <label>密码</label>
        <input v-model="form.password" type="password" placeholder="请输入密码" required />
      </div>
      <div class="form-item inline">
        <label><input type="checkbox" v-model="remember" /> 记住我（仅保存账号）</label>
      </div>
      <button type="submit" class="primary">登录</button>
      <p class="tips">还没有账号？<router-link to="/register">去注册</router-link></p>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({ identity: '', password: '' })
const remember = ref(false)

async function onSubmit () {
  try {
    const { data } = await api.login({ identity: form.identity, password: form.password })
    userStore.setUser(data.id, data.username)
    await userStore.refreshProfile()
    if (remember.value) {
      try { localStorage.setItem('remember_identity', form.identity) } catch {}
    } else {
      try { localStorage.removeItem('remember_identity') } catch {}
    }
    router.replace('/profile')
  } catch (err) {
    alert(err?.response?.data?.detail || '登录失败')
  }
}

onMounted(() => {
  try {
    const v = localStorage.getItem('remember_identity')
    if (v) { form.identity = v; remember.value = true }
  } catch {}
})
</script>

<style scoped>
.auth-container { max-width: 420px; margin: 24px auto; padding: 24px; border: 1px solid #eee; border-radius: 8px; }
.form-item { margin-bottom: 16px; }
.form-item.inline { display: flex; align-items: center; }.form-item.inline label { margin-bottom: 0; display: inline-flex; align-items: center; gap: 8px; color: #555; }
.form-item.inline input[type="checkbox"] { width: auto; }
label { display: block; margin-bottom: 6px; color: #555; }
input { width: 100%; padding: 10px 12px; border: 1px solid #ccc; border-radius: 6px; }
button.primary { width: 100%; padding: 10px; border: none; border-radius: 6px; background: #42b983; color: #fff; font-weight: 600; cursor: pointer; }
.tips { margin-top: 12px; text-align: center; color: #666; }
</style>