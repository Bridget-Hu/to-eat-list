<template>
  <div class="app">
    <header class="top-bar">
      <div class="logo" @click="goHome">校园吃饭决策助手</div>
      <button class="nav-btn" @click="goUpload">批量导入菜品数据</button>
    </header>

    <HomePage v-if="currentPage === 'home'" @go-upload="goUpload" />
    <UploadPage v-else @go-home="goHome" />
  </div>
</template>

<script setup>
import { ref } from "vue";

import HomePage from "./pages/Home/index.vue";
import UploadPage from "./pages/Upload/index.vue";

const currentPage = ref(window.location.pathname === "/upload" ? "upload" : "home");

function goHome() {
  currentPage.value = "home";
  window.history.pushState({}, "", "/");
}

function goUpload() {
  currentPage.value = "upload";
  window.history.pushState({}, "", "/upload");
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, #e8f4ff 0, transparent 32%),
    linear-gradient(135deg, #f8fbff 0%, #eef4f8 100%);
  color: #1f2937;
  font-family: "Microsoft YaHei", sans-serif;
}

.top-bar {
  height: 72px;
  padding: 0 8%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 20px;
  font-weight: 800;
  cursor: pointer;
}

.nav-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 999px;
  background: #ffffff;
  color: #2563eb;
  font-size: 15px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.12);
}
</style>