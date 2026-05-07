<script setup>
defineProps({
  badge: {
    type: String,
    default: "暂无内容"
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ""
  }
});
</script>

<template>
  <div class="empty-state">
    <span class="empty-state__badge">{{ badge }}</span>
    <h2 class="empty-state__title">{{ title }}</h2>
    <p v-if="description" class="empty-state__description">{{ description }}</p>

    <div v-if="$slots.actions" class="empty-state__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<style scoped>
.empty-state {
  display: grid;
  justify-items: start;
  gap: 12px;
}

.empty-state__badge {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 7px 11px;
  border-radius: 999px;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background: rgba(17, 75, 95, 0.08);
}

.empty-state__title {
  margin: 0;
  font-size: 24px;
  line-height: 1.18;
}

.empty-state__description {
  max-width: 620px;
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.7;
}

.empty-state__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
