import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "../api";

export const useUserStore = defineStore("user", () => {
  const userId = ref(null);
  const username = ref("体验用户");
  const profile = ref(null);

  async function init() {
    // 读取本地登录态；若后端不存在该用户则自动重新注册
    const savedId = localStorage.getItem("user_id");
    const savedName = localStorage.getItem("username");
    if (savedId) {
      const idNum = Number(savedId);
      try {
        const { data } = await api.getUser(idNum);
        userId.value = data.id;
        username.value = data.username;
        profile.value = data;
        return;
      } catch (err) {
        localStorage.removeItem("user_id");
        localStorage.removeItem("username");
      }
    }

    // 无本地用户或本地用户已失效：注册体验用户
    try {
      const ts = Date.now();
      const tempUsername = `体验用户-${ts}`;
      const tempEmail = `demo_user_${ts}@example.com`;
      const { data } = await api.registerUser({
        username: tempUsername,
        email: tempEmail,
        password: "Passw0rd!",
        full_name: "体验用户",
        phone: "13800000000",
        address: "北京朝阳区",
      });
      userId.value = data.id;
      username.value = data.username;
      localStorage.setItem("user_id", String(data.id));
      localStorage.setItem("username", data.username);
    } catch (err) {
      console.error("初始化用户失败:", err);
    }
  }

  function setUser(id, name) {
    userId.value = id;
    username.value = name;
    localStorage.setItem("user_id", String(id));
    if (name) localStorage.setItem("username", name);
  }

  async function refreshProfile() {
    if (!userId.value) return;
    try {
      const { data } = await api.getUser(userId.value);
      profile.value = data;
      username.value = data.username;
    } catch (err) {
      console.error("刷新用户信息失败:", err);
    }
  }

  // 新增：登出并清理本地登录态
  function logout() {
    userId.value = null;
    username.value = "体验用户";
    localStorage.removeItem("user_id");
    localStorage.removeItem("username");
  }

  return {
    userId,
    username,
    profile,
    init,
    setUser,
    refreshProfile,
    logout,
  };
});

