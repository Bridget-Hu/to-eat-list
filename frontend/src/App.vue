<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import { navigationItems } from "./router";

const route = useRoute();

const currentLabel = computed(() => route.meta?.label ?? "首页");
</script>

<template>
  <div class="app-shell">
    <div class="ambient ambient-one"></div>
    <div class="ambient ambient-two"></div>

    <header class="app-header">
      <router-link class="brand" to="/">
        <span class="brand-mark">TL</span>

        <div class="brand-copy">
          <strong>To-Eat-List</strong>
          <span>{{ currentLabel }}</span>
        </div>
      </router-link>

      <nav class="nav-links" aria-label="主导航">
        <router-link
          v-for="item in navigationItems"
          :key="item.to"
          :to="item.to"
          class="nav-link"
        >
          {{ item.label }}
        </router-link>
      </nav>
    </header>

    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<style>
:root {
  --page-bg: #f6ead9;
  --panel-bg: rgba(255, 251, 245, 0.82);
  --panel-strong: rgba(255, 255, 255, 0.96);
  --border-soft: rgba(17, 75, 95, 0.14);
  --shadow-soft: 0 24px 70px rgba(69, 50, 36, 0.14);
  --text-primary: #16323f;
  --text-secondary: #5d6b73;
  --accent-primary: #114b5f;
  --accent-secondary: #ff8c42;
  --accent-soft: #ffe0c2;
  --success: #1f8a70;
  --danger: #c44536;
}

* {
  box-sizing: border-box;
}

html {
  background: var(--page-bg);
}

body {
  margin: 0;
  min-height: 100vh;
  overflow-x: hidden;
  background:
    radial-gradient(circle at top left, rgba(255, 199, 146, 0.42), transparent 34%),
    radial-gradient(circle at right 12%, rgba(17, 75, 95, 0.12), transparent 26%),
    linear-gradient(180deg, #fff7ed 0%, #f8efe4 54%, #f3e6d6 100%);
  color: var(--text-primary);
  font-family: "Avenir Next", "PingFang SC", "Microsoft YaHei", "Trebuchet MS", sans-serif;
}

#app {
  min-height: 100vh;
}

a {
  color: inherit;
  text-decoration: none;
}

button,
input,
select,
textarea {
  font: inherit;
}

.app-shell {
  position: relative;
  min-height: 100vh;
  padding: 24px;
}

.ambient {
  position: fixed;
  z-index: 0;
  border-radius: 999px;
  filter: blur(10px);
  pointer-events: none;
}

.ambient-one {
  top: 72px;
  right: -80px;
  width: 260px;
  height: 260px;
  background: rgba(255, 140, 66, 0.18);
}

.ambient-two {
  left: -70px;
  bottom: 12%;
  width: 220px;
  height: 220px;
  background: rgba(17, 75, 95, 0.12);
}

.app-header,
.app-main {
  position: relative;
  z-index: 1;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  max-width: 1280px;
  margin: 0 auto 20px;
  padding: 18px 22px;
  border: 1px solid var(--border-soft);
  border-radius: 24px;
  background: rgba(255, 251, 245, 0.72);
  box-shadow: 0 18px 40px rgba(69, 50, 36, 0.1);
  backdrop-filter: blur(18px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 18px;
  color: white;
  font-weight: 900;
  letter-spacing: 0.08em;
  background: linear-gradient(135deg, var(--accent-primary), #1b7a8f);
  box-shadow: 0 16px 30px rgba(17, 75, 95, 0.2);
}

.brand-copy {
  display: grid;
  gap: 3px;
}

.brand-copy strong {
  font-size: 18px;
  letter-spacing: 0.04em;
}

.brand-copy span {
  color: var(--text-secondary);
  font-size: 13px;
}

.nav-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.nav-link {
  padding: 11px 16px;
  border-radius: 999px;
  color: var(--text-secondary);
  font-weight: 700;
  transition:
    transform 0.2s ease,
    background 0.2s ease,
    color 0.2s ease,
    box-shadow 0.2s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--accent-primary);
  background: rgba(17, 75, 95, 0.08);
  box-shadow: inset 0 0 0 1px rgba(17, 75, 95, 0.08);
}

.nav-link:hover {
  transform: translateY(-1px);
}

.app-main {
  max-width: 1280px;
  margin: 0 auto;
}

.page {
  display: grid;
  gap: 24px;
}

.panel {
  border: 1px solid var(--border-soft);
  border-radius: 28px;
  background: var(--panel-bg);
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(16px);
}

.section-kicker {
  margin: 0 0 12px;
  color: var(--accent-primary);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.section-title {
  margin: 0;
  font-size: clamp(30px, 5vw, 54px);
  line-height: 1.04;
}

.section-desc {
  margin: 16px 0 0;
  color: var(--text-secondary);
  font-size: 16px;
  line-height: 1.85;
}

.primary-button,
.secondary-button,
.ghost-button {
  border: none;
  border-radius: 999px;
  padding: 13px 22px;
  font-weight: 800;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease,
    opacity 0.2s ease;
}

.primary-button:hover,
.secondary-button:hover,
.ghost-button:hover {
  transform: translateY(-2px);
}

.primary-button:disabled,
.secondary-button:disabled,
.ghost-button:disabled {
  opacity: 0.58;
  cursor: not-allowed;
  transform: none;
}

.primary-button {
  color: white;
  background: linear-gradient(135deg, var(--accent-primary), #1b7a8f);
  box-shadow: 0 16px 36px rgba(17, 75, 95, 0.2);
}

.secondary-button {
  color: var(--accent-primary);
  background: rgba(17, 75, 95, 0.08);
}

.ghost-button {
  color: var(--accent-primary);
  background: rgba(255, 255, 255, 0.78);
  box-shadow: inset 0 0 0 1px rgba(17, 75, 95, 0.1);
}

.field-label {
  display: grid;
  gap: 9px;
  color: var(--text-primary);
  font-weight: 800;
}

.field-input,
.field-select,
.field-textarea {
  width: 100%;
  border: 1px solid rgba(17, 75, 95, 0.14);
  border-radius: 16px;
  padding: 13px 15px;
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.92);
  outline: none;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.field-input:focus,
.field-select:focus,
.field-textarea:focus {
  border-color: rgba(17, 75, 95, 0.48);
  box-shadow: 0 0 0 4px rgba(17, 75, 95, 0.08);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 800;
}

.status-pill.success {
  color: var(--success);
  background: rgba(31, 138, 112, 0.12);
}

.status-pill.warning {
  color: #b26120;
  background: rgba(255, 140, 66, 0.18);
}

.status-pill.danger {
  color: var(--danger);
  background: rgba(196, 69, 54, 0.12);
}

.status-pill.neutral {
  color: var(--text-secondary);
  background: rgba(17, 75, 95, 0.06);
}

@media (max-width: 920px) {
  .app-shell {
    padding: 16px;
  }

  .app-header {
    flex-direction: column;
    align-items: stretch;
  }

  .nav-links {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .app-header {
    padding: 16px;
    border-radius: 20px;
  }

  .brand {
    align-items: flex-start;
  }

  .nav-links {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .nav-link {
    text-align: center;
  }
}
</style>
