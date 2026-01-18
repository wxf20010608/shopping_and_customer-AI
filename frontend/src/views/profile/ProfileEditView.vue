<template>
  <div class="profile-edit">
    <h2>编辑个人信息</h2>
    <form @submit.prevent="onSubmit">
      <div class="form-item"><label>用户名</label><input v-model="form.username" required /></div>
      <div class="form-item"><label>邮箱</label><input v-model="form.email" type="email" required /></div>
      <div class="form-item"><label>姓名</label><input v-model="form.full_name" /></div>
      <div class="form-item"><label>电话</label><input v-model="form.phone" /></div>
      <button type="submit" class="primary">保存</button>
    </form>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({ id: null, username: '', email: '', full_name: '', phone: '' })

onMounted(async () => {
  const id = userStore.userId
  if (!id) return router.replace('/login')
  const name = userStore.username
  Object.assign(form, { id, username: name })
})

async function onSubmit () {
  try {
    const { data } = await api.updateUser(form.id, {
      username: form.username,
      email: form.email,
      full_name: form.full_name,
      phone: form.phone,
    })
    userStore.setUser(data.id, data.username)
    alert('更新成功')
    router.replace('/profile')
  } catch (err) {
    alert(err?.response?.data?.detail || '更新失败')
  }
}
</script>

<style scoped>
.profile-edit { max-width: 560px; margin: 24px auto; padding: 24px; border: 1px solid #eee; border-radius: 8px; }
.form-item { margin-bottom: 16px; }
label { display: block; margin-bottom: 6px; color: #555; }
input { width: 100%; padding: 10px 12px; border: 1px solid #ccc; border-radius: 6px; }
button.primary { padding: 10px 16px; border: none; border-radius: 6px; background: #42b983; color: #fff; font-weight: 600; cursor: pointer; }
</style>