import { createRouter, createWebHashHistory } from "vue-router";

import HomePage from "../pages/Home/index.vue";
import HistoryPage from "../pages/History/index.vue";
import RecommendPage from "../pages/Recommend/index.vue";
import UploadPage from "../pages/Upload/index.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: HomePage,
    meta: {
      label: "首页"
    }
  },
  {
    path: "/upload",
    name: "Upload",
    component: UploadPage,
    meta: {
      label: "菜品管理"
    }
  },
  {
    path: "/recommend",
    name: "Recommend",
    component: RecommendPage,
    meta: {
      label: "生成推荐"
    }
  },
  {
    path: "/history",
    name: "History",
    component: HistoryPage,
    meta: {
      label: "历史记录"
    }
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

export const navigationItems = routes.map((route) => ({
  to: route.path,
  label: route.meta?.label ?? route.name
}));

export default router;
