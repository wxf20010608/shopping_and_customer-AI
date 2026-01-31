<template>
  <div>
    <header :class="['header', { compact: isChatRoute }]">
      <div class="container header-inner">
        <h1>智慧商城</h1>
        <nav class="nav">
          <RouterLink to="/">首页</RouterLink>
          <RouterLink to="/cart">购物车</RouterLink>
          <RouterLink to="/orders">订单</RouterLink>

          <template v-if="isLoggedIn">
            <RouterLink to="/profile">个人中心（{{ displayName }}）</RouterLink>
            <a href="#" @click.prevent="logoutAndGo">退出登录</a>
          </template>
          <template v-else>
            <RouterLink to="/login">登录</RouterLink>
            <RouterLink to="/register">注册</RouterLink>
          </template>
          <RouterLink to="/wishlist">心愿单</RouterLink>
        </nav>
      </div>
    </header>
    <main class="container">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from "./stores/user";
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const displayName = computed(() => userStore.profile?.username || userStore.username)
const isLoggedIn = computed(() => !!userStore.userId)
const isChatRoute = computed(() => route.path.startsWith('/chat'))




function logoutAndGo(){
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.header {
  background-color: #1d4ed8;
  color: #fff;
  padding: 16px 0;
  margin-bottom: 16px;
  position: sticky;
  top: 0;
  z-index: 1000;
}
.header.compact { padding: 8px 0; margin-bottom: 8px; }

.header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav {
  display: flex;
  gap: 16px;
}

.nav a {
  color: #fff;
  font-weight: 500;
}

.nav a.router-link-active {
  text-decoration: underline;
}
</style>

