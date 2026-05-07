<script setup>
import { computed } from "vue";

defineOptions({
  inheritAttrs: false
});

const props = defineProps({
  as: {
    type: String,
    default: "section"
  },
  padding: {
    type: String,
    default: "md"
  },
  tone: {
    type: String,
    default: "default"
  },
  interactive: {
    type: Boolean,
    default: false
  }
});

const cardClasses = computed(() => [
  `app-card--${props.padding}`,
  `app-card--${props.tone}`,
  props.interactive && "app-card--interactive"
]);
</script>

<template>
  <component
    :is="as"
    class="app-card"
    :class="cardClasses"
    v-bind="$attrs"
  >
    <slot />
  </component>
</template>

<style scoped>
.app-card {
  min-width: 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(16px);
}

.app-card--none {
  padding: 0;
}

.app-card--sm {
  padding: 16px;
}

.app-card--md {
  padding: 22px;
}

.app-card--lg {
  padding: 28px;
}

.app-card--default {
  background: var(--color-surface);
}

.app-card--muted {
  background: var(--color-surface-muted);
}

.app-card--accent {
  background:
    radial-gradient(circle at top right, rgba(240, 154, 74, 0.12), transparent 34%),
    var(--color-surface-strong);
}

.app-card--interactive {
  transition:
    transform var(--transition-fast),
    box-shadow var(--transition-fast),
    border-color var(--transition-fast);
}

.app-card--interactive:hover {
  transform: translateY(-2px);
  border-color: rgba(17, 75, 95, 0.18);
  box-shadow: var(--shadow-medium);
}

@media (max-width: 640px) {
  .app-card--lg {
    padding: 22px;
  }
}
</style>
