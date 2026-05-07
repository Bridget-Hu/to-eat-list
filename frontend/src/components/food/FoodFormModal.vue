<script setup>
import { reactive, ref, watch } from "vue";
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NModal,
  NSelect
} from "naive-ui";

import { foodCategoryOptions } from "@/api/foods";

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: "create"
  },
  food: {
    type: Object,
    default: null
  },
  saving: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(["close", "submit"]);

const formRef = ref(null);
const formModel = reactive(createEmptyForm());

const rules = {
  name: {
    required: true,
    validator(_, value) {
      if (!String(value || "").trim()) {
        return new Error("请输入菜名");
      }

      return true;
    },
    trigger: ["input", "blur"]
  },
  price: {
    required: true,
    validator(_, value) {
      if (value === null || value === undefined || Number(value) <= 0) {
        return new Error("价格必须大于 0");
      }

      return true;
    },
    trigger: ["blur", "change"]
  }
};

function createEmptyForm() {
  return {
    name: "",
    store: "",
    price: null,
    category: "其他",
    taste_tags: "",
    health_tags: "",
    note: ""
  };
}

function applyFood(food) {
  const nextForm = food
    ? {
        name: food.name || "",
        store: food.store || "",
        price: food.price ?? null,
        category: food.category || "其他",
        taste_tags: food.taste_tags || "",
        health_tags: food.health_tags || "",
        note: food.note || ""
      }
    : createEmptyForm();

  Object.assign(formModel, nextForm);
  formRef.value?.restoreValidation();
}

async function handleSubmit() {
  try {
    await formRef.value?.validate();
  } catch {
    return;
  }

  emit("submit", {
    name: formModel.name.trim(),
    store: formModel.store.trim(),
    price: Number(formModel.price),
    category: formModel.category || "其他",
    taste_tags: formModel.taste_tags.trim(),
    health_tags: formModel.health_tags.trim(),
    note: formModel.note.trim()
  });
}

function handleClose() {
  emit("close");
}

watch(
  () => [props.show, props.food],
  () => {
    if (props.show) {
      applyFood(props.food);
    }
  },
  { immediate: true }
);
</script>

<template>
  <NModal
    :show="show"
    preset="card"
    :title="mode === 'edit' ? '编辑菜品' : '新增菜品'"
    class="food-form-modal"
    @update:show="handleClose"
  >
    <NForm ref="formRef" :model="formModel" :rules="rules" label-placement="top">
      <div class="food-form-grid">
        <NFormItem label="菜名" path="name">
          <NInput v-model:value="formModel.name" placeholder="例如 香煎鸡胸饭" />
        </NFormItem>

        <NFormItem label="店名" path="store">
          <NInput v-model:value="formModel.store" placeholder="例如 轻食窗口" />
        </NFormItem>

        <NFormItem label="价格" path="price">
          <NInputNumber
            v-model:value="formModel.price"
            :min="0.1"
            :precision="1"
            placeholder="例如 18.5"
            clearable
            class="food-form-number"
          />
        </NFormItem>

        <NFormItem label="分类" path="category">
          <NSelect
            v-model:value="formModel.category"
            :options="foodCategoryOptions"
            placeholder="请选择分类"
          />
        </NFormItem>

        <NFormItem label="口味标签" path="taste_tags">
          <NInput
            v-model:value="formModel.taste_tags"
            placeholder="例如 清淡、微辣、咸香"
          />
        </NFormItem>

        <NFormItem label="健康标签" path="health_tags">
          <NInput
            v-model:value="formModel.health_tags"
            placeholder="例如 高蛋白、低脂、蔬菜多"
          />
        </NFormItem>

        <NFormItem label="备注" path="note" class="food-form-grid__full">
          <NInput
            v-model:value="formModel.note"
            type="textarea"
            placeholder="记录真实体验，例如适合赶时间、减脂友好"
            :autosize="{ minRows: 3, maxRows: 5 }"
          />
        </NFormItem>
      </div>

      <div class="food-form-actions">
        <NButton quaternary @click="handleClose">取消</NButton>
        <NButton type="primary" :loading="saving" @click="handleSubmit">
          {{ mode === "edit" ? "保存修改" : "新增菜品" }}
        </NButton>
      </div>
    </NForm>
  </NModal>
</template>

<style scoped>
.food-form-modal {
  width: min(720px, calc(100vw - 32px));
}

.food-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 16px;
}

.food-form-grid__full {
  grid-column: 1 / -1;
}

.food-form-number {
  width: 100%;
}

.food-form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

@media (max-width: 680px) {
  .food-form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
