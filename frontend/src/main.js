import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "./styles.css";
import { useUserStore } from "./stores/user";

const app = createApp(App);

const pinia = createPinia();
app.use(pinia);
app.use(router);

const userStore = useUserStore();
app.mount("#app");
void userStore.init();

