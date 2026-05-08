<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
});
</script>

<template>
  <nav class="app-nav" aria-label="主导航">
    <router-link
      v-for="item in items"
      :key="item.to"
      :to="item.to"
      class="app-nav__link"
    >
      {{ item.label }}
    </router-link>
  </nav>
</template>

<style scoped>
.app-nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.app-nav__link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 9px 14px;
  border-radius: 999px;
  color: var(--color-text-muted);
  font-weight: 700;
  white-space: nowrap;
  transition:
    color var(--transition-fast),
    background var(--transition-fast),
    transform var(--transition-fast);
}

.app-nav__link:hover,
.app-nav__link.router-link-active {
  color: var(--color-primary);
  background: rgba(17, 75, 95, 0.08);
}

.app-nav__link:hover {
  transform: translateY(-1px);
}

@media (max-width: 720px) {
  .app-nav {
    justify-content: flex-start;
  }
}
</style>
