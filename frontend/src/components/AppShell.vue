<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import AppNav from "./AppNav.vue";
import { navigationItems } from "@/router";

const route = useRoute();

const currentLabel = computed(() => route.meta?.label ?? "首页");
</script>

<template>
  <div class="app-shell">
    <div class="app-shell__glow app-shell__glow--warm"></div>
    <div class="app-shell__glow app-shell__glow--cool"></div>

    <header class="app-shell__header">
      <router-link class="brand" to="/">
        <span class="brand__mark">TL</span>

        <div class="brand__copy">
          <strong>To-Eat-List</strong>
          <span>校园饮食决策助手</span>
        </div>
      </router-link>

      <div class="app-shell__nav-group">
        <span class="status-pill status-pill--neutral">
          当前页面：{{ currentLabel }}
        </span>
        <AppNav :items="navigationItems" />
      </div>
    </header>

    <main class="app-shell__main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  position: relative;
  min-height: 100vh;
  padding: var(--page-gutter);
}

.app-shell__glow {
  position: fixed;
  z-index: 0;
  border-radius: 999px;
  filter: blur(12px);
  pointer-events: none;
}

.app-shell__glow--warm {
  top: 72px;
  right: -90px;
  width: 260px;
  height: 260px;
  background: rgba(240, 154, 74, 0.18);
}

.app-shell__glow--cool {
  left: -80px;
  bottom: 12%;
  width: 220px;
  height: 220px;
  background: rgba(17, 75, 95, 0.12);
}

.app-shell__header,
.app-shell__main {
  position: relative;
  z-index: 1;
}

.app-shell__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  max-width: var(--page-max-width);
  margin: 0 auto 18px;
  padding: 14px 18px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  background: rgba(255, 251, 245, 0.78);
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(18px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.brand__mark {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 16px;
  color: #fff;
  font-weight: 900;
  letter-spacing: 0.08em;
  background: linear-gradient(135deg, var(--color-primary), #1d7285);
  box-shadow: var(--shadow-glow);
}

.brand__copy {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.brand__copy strong {
  font-size: 18px;
  letter-spacing: 0.04em;
}

.brand__copy span {
  color: var(--color-text-muted);
  font-size: 13px;
}

.app-shell__nav-group {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  min-width: 0;
}

.app-shell__main {
  max-width: var(--page-max-width);
  margin: 0 auto;
}

@media (max-width: 960px) {
  .app-shell__header {
    flex-direction: column;
    align-items: stretch;
  }

  .app-shell__nav-group {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .app-shell__header {
    padding: 14px;
    border-radius: var(--radius-lg);
  }

  .brand {
    align-items: flex-start;
  }

  .brand__copy strong {
    font-size: 17px;
  }
}
</style>
