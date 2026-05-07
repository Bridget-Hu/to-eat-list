<script setup>
defineProps({
  eyebrow: {
    type: String,
    default: ""
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ""
  },
  titleTag: {
    type: String,
    default: "h1"
  },
  compact: {
    type: Boolean,
    default: false
  }
});
</script>

<template>
  <header class="page-header" :class="{ 'page-header--compact': compact }">
    <div class="page-header__copy">
      <p v-if="eyebrow" class="eyebrow">{{ eyebrow }}</p>
      <component :is="titleTag" class="page-header__title">
        {{ title }}
      </component>
      <p v-if="description" class="page-header__description">
        {{ description }}
      </p>

      <div v-if="$slots.meta" class="page-header__meta">
        <slot name="meta" />
      </div>
    </div>

    <div v-if="$slots.actions" class="page-header__actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  min-width: 0;
}

.page-header__copy {
  display: grid;
  gap: 10px;
  min-width: 0;
}

.page-header__title {
  margin: 0;
  font-size: clamp(28px, 4vw, 42px);
  line-height: 1.08;
  letter-spacing: -0.03em;
}

.page-header--compact .page-header__title {
  font-size: clamp(24px, 3.6vw, 34px);
}

.page-header__description {
  max-width: 720px;
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.75;
}

.page-header__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.page-header__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 820px) {
  .page-header {
    flex-direction: column;
  }

  .page-header__actions {
    justify-content: flex-start;
  }
}
</style>
