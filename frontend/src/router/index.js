import { createRouter, createWebHashHistory } from "vue-router";

import HomePage from "../pages/Home/index.vue";
import UploadPage from "../pages/Upload/index.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: HomePage
  },
  {
    path: "/upload",
    name: "Upload",
    component: UploadPage
  }
];

console.log("路由加载成功", routes);

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

export default router;