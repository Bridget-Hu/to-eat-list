<script setup>
import AppCard from "./AppCard.vue";

defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  hint: {
    type: String,
    default: ""
  },
  tone: {
    type: String,
    default: "default"
  }
});
</script>

<template>
  <AppCard class="stat-card" :tone="tone" padding="sm">
    <span class="stat-card__label">{{ label }}</span>
    <strong class="stat-card__value">{{ value }}</strong>
    <p v-if="hint" class="stat-card__hint">{{ hint }}</p>
  </AppCard>
</template>

<style scoped>
.stat-card {
  display: grid;
  gap: 10px;
}

.stat-card__label {
  color: var(--color-text-muted);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.stat-card__value {
  font-size: clamp(24px, 3vw, 30px);
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.stat-card__hint {
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.6;
}
</style>
