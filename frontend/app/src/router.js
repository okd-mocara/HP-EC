import { createRouter, createWebHistory } from "vue-router";
import TopPage from "./pages/TopPage/MainPage.vue";
import ShopPage from "./pages/ShopPage/MainPage.vue";

const routes = [
  { path: "/", name: "top", component: TopPage },
  { path: "/shop", name: "shop", component: ShopPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
