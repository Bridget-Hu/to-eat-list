import { computed, ref } from "vue";
import { defineStore } from "pinia";

import { errorCopy } from "@/utils/copy";

const STORAGE_KEY = "to_eat_list_saved_conditions";

function createConditionId() {
  if (window.crypto?.randomUUID) {
    return window.crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function normalizeForm(form = {}) {
  return {
    budget: Number(form.budget ?? 60),
    taste: form.taste || "",
    dislike: form.dislike || "",
    want: form.want || "",
    goal: form.goal || "",
    hadMilkTea: Boolean(form.hadMilkTea)
  };
}

function normalizeCondition(item) {
  if (!item || typeof item !== "object") {
    return null;
  }

  const name = String(item.name || "").trim();

  if (!name) {
    return null;
  }

  const now = new Date().toISOString();

  return {
    id: String(item.id || createConditionId()),
    name,
    form: normalizeForm(item.form),
    createdAt: item.createdAt || now,
    updatedAt: item.updatedAt || item.createdAt || now
  };
}

export const useSavedConditionsStore = defineStore("savedConditions", () => {
  const conditions = ref([]);
  const storageError = ref("");

  const count = computed(() => conditions.value.length);

  function loadConditions() {
    storageError.value = "";

    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);

      if (!raw) {
        conditions.value = [];
        return;
      }

      const parsed = JSON.parse(raw);

      if (!Array.isArray(parsed)) {
        throw new Error("Invalid saved conditions payload");
      }

      conditions.value = parsed.map(normalizeCondition).filter(Boolean);
    } catch {
      conditions.value = [];
      storageError.value = errorCopy.savedConditionsRead;

      try {
        window.localStorage.removeItem(STORAGE_KEY);
      } catch {
        // Ignore secondary localStorage cleanup failures.
      }
    }
  }

  function persistConditions() {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(conditions.value));
      storageError.value = "";
      return true;
    } catch {
      storageError.value = errorCopy.savedConditionsWrite;
      return false;
    }
  }

  function saveCondition(name, form) {
    const now = new Date().toISOString();
    const condition = {
      id: createConditionId(),
      name: name.trim(),
      form: normalizeForm(form),
      createdAt: now,
      updatedAt: now
    };
    const previousConditions = conditions.value;

    conditions.value = [condition, ...conditions.value];

    if (!persistConditions()) {
      conditions.value = previousConditions;
      return null;
    }

    return condition;
  }

  function deleteCondition(conditionId) {
    const previousConditions = conditions.value;

    conditions.value = conditions.value.filter((item) => item.id !== conditionId);

    if (!persistConditions()) {
      conditions.value = previousConditions;
      return false;
    }

    return true;
  }

  return {
    conditions,
    count,
    storageError,
    loadConditions,
    saveCondition,
    deleteCondition
  };
});
