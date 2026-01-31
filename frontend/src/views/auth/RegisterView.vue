<template>
  <div class="auth-container">
    <h2>注册</h2>
    <form @submit.prevent="onSubmit">
      <div class="form-item">
        <label>用户名</label>
        <input v-model="form.username" placeholder="请输入用户名" required />
      </div>
      <div class="form-item">
        <label>邮箱</label>
        <input v-model="form.email" type="email" placeholder="请输入邮箱" required />
      </div>
      <div class="form-item">
        <label>密码</label>
        <input v-model="form.password" type="password" placeholder="请输入密码" required />
      </div>
      <div class="form-item">
        <label>姓名</label>
        <input v-model="form.full_name" placeholder="请输入姓名" />
      </div>
      <div class="form-item">
        <label>电话</label>
        <input v-model="form.phone" placeholder="请输入电话" />
      </div>
      <button type="submit" class="primary">注册</button>
      <p class="tips">已有账号？<router-link to="/login">去登录</router-link></p>
    </form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({ username: '', email: '', password: '', full_name: '', phone: '' })

async function onSubmit () {
  try {
    const { data } = await api.registerUser(form)
    userStore.setUser(data.id, data.username)
    router.replace('/profile')
  } catch (err) {
    alert(err?.response?.data?.detail || '注册失败')
  }
}
</script>

<style scoped>
.auth-container { max-width: 420px; margin: 24px auto; padding: 24px; border: 1px solid #eee; border-radius: 8px; }
.form-item { margin-bottom: 16px; }
label { display: block; margin-bottom: 6px; color: #555; }
input { width: 100%; padding: 10px 12px; border: 1px solid #ccc; border-radius: 6px; }
button.primary { width: 100%; padding: 10px; border: none; border-radius: 6px; background: #42b983; color: #fff; font-weight: 600; cursor: pointer; }
.tips { margin-top: 12px; text-align: center; color: #666; }
</style>