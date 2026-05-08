<script setup>
import { computed, onMounted, ref } from "vue";
import {
  NAlert,
  NButton,
  NEmpty,
  NInput,
  NPopconfirm,
  NSelect,
  useMessage
} from "naive-ui";

import {
  batchDeleteFoods,
  createFood,
  deleteFood,
  foodCategoryOptions,
  listFoods,
  updateFood,
  uploadFoodFile
} from "@/api/foods";
import AppCard from "@/components/AppCard.vue";
import FoodFormModal from "@/components/food/FoodFormModal.vue";
import FoodTable from "@/components/food/FoodTable.vue";
import PageHeader from "@/components/PageHeader.vue";
import StatCard from "@/components/StatCard.vue";

defineOptions({
  name: "UploadPage"
});

const message = useMessage();

const foods = ref([]);
const loadingFoods = ref(false);
const savingFood = ref(false);
const deletingFoods = ref(false);
const selectedFoodIds = ref([]);
const keyword = ref("");
const selectedCategory = ref(null);
const errorMessage = ref("");
const uploadSummary = ref("");
const selectedFileName = ref("");
const fileInput = ref(null);
const showFoodModal = ref(false);
const modalMode = ref("create");
const activeFood = ref(null);

const filteredFoods = computed(() => {
  const search = keyword.value.trim().toLowerCase();

  return foods.value.filter((food) => {
    const matchesCategory =
      !selectedCategory.value || food.category === selectedCategory.value;

    if (!matchesCategory) {
      return false;
    }

    if (!search) {
      return true;
    }

    const text = [
      food.name,
      food.store,
      food.category,
      food.taste_tags,
      food.health_tags,
      food.note
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return text.includes(search);
  });
});

const categoryFilterOptions = computed(() => {
  const dynamicOptions = new Set(
    foods.value.map((food) => food.category).filter(Boolean)
  );

  const knownOptions = foodCategoryOptions.map((item) => item.value);

  return Array.from(new Set([...knownOptions, ...dynamicOptions])).map((value) => ({
    label: value,
    value
  }));
});

const priceStats = computed(() => {
  const foodsWithPrice = foods.value.filter((food) => Number(food.price) > 0);

  if (!foodsWithPrice.length) {
    return "0.0";
  }

  const totalPrice = foodsWithPrice.reduce(
    (sum, food) => sum + Number(food.price || 0),
    0
  );

  return (totalPrice / foodsWithPrice.length).toFixed(1);
});

const topCategory = computed(() => {
  if (!foods.value.length) {
    return "暂无";
  }

  const counts = foods.value.reduce((map, food) => {
    const key = food.category || "其他";
    map[key] = (map[key] || 0) + 1;
    return map;
  }, {});

  return Object.entries(counts).sort((left, right) => right[1] - left[1])[0][0];
});

const selectedFoodCount = computed(() => selectedFoodIds.value.length);

async function loadFoods() {
  loadingFoods.value = true;
  errorMessage.value = "";

  try {
    const response = await listFoods();
    foods.value = Array.isArray(response?.data) ? response.data : [];
    selectedFoodIds.value = selectedFoodIds.value.filter((foodId) =>
      foods.value.some((food) => food.id === foodId)
    );
  } catch (error) {
    errorMessage.value = error.message || "获取菜品列表失败";
  } finally {
    loadingFoods.value = false;
  }
}

function openCreateModal() {
  modalMode.value = "create";
  activeFood.value = null;
  showFoodModal.value = true;
}

function openEditModal(food) {
  modalMode.value = "edit";
  activeFood.value = { ...food };
  showFoodModal.value = true;
}

function closeFoodModal() {
  showFoodModal.value = false;
  activeFood.value = null;
}

async function handleSubmitFood(payload) {
  savingFood.value = true;

  try {
    if (modalMode.value === "edit" && activeFood.value?.id) {
      await updateFood(activeFood.value.id, payload);
      message.success("菜品已更新");
    } else {
      await createFood(payload);
      message.success("菜品已新增");
    }

    closeFoodModal();
    await loadFoods();
  } catch (error) {
    message.error(error.message || "保存菜品失败");
  } finally {
    savingFood.value = false;
  }
}

async function handleDeleteFood(food) {
  try {
    await deleteFood(food.id);
    message.success(`已删除“${food.name}”`);
    await loadFoods();
  } catch (error) {
    message.error(error.message || "删除菜品失败");
  }
}

async function handleBatchDeleteFoods() {
  if (!selectedFoodIds.value.length) {
    return;
  }

  deletingFoods.value = true;

  try {
    const response = await batchDeleteFoods(selectedFoodIds.value);
    message.success(response?.message || `已删除 ${selectedFoodIds.value.length} 条菜品`);
    selectedFoodIds.value = [];
    await loadFoods();
  } catch (error) {
    message.error(error.message || "批量删除菜品失败");
  } finally {
    deletingFoods.value = false;
  }
}

function triggerUpload() {
  fileInput.value?.click();
}

async function handleFileChange(event) {
  const file = event.target.files?.[0];

  if (!file) {
    return;
  }

  selectedFileName.value = file.name;
  uploadSummary.value = "";

  try {
    const response = await uploadFoodFile(file);
    foods.value = Array.isArray(response?.data) ? response.data : [];
    selectedFoodIds.value = [];
    uploadSummary.value = `导入成功，当前菜品库共 ${response?.count ?? foods.value.length} 条数据。`;
    message.success("菜品文件导入成功");
  } catch (error) {
    message.error(error.message || "导入菜品文件失败");
  } finally {
    event.target.value = "";
  }
}

onMounted(() => {
  loadFoods();
});
</script>

<template>
  <div class="page foods-page">
    <input
      ref="fileInput"
      type="file"
      accept=".txt,.csv,.json"
      hidden
      @change="handleFileChange"
    >

    <AppCard padding="md" tone="accent">
      <PageHeader
        eyebrow="Food Management"
        title="菜品管理"
        description="首屏直接进入新增、搜索、筛选和编辑，不再把导入入口放成大面积宣传区。文件导入仍然保留，但现在只是补充入口。"
        compact
      >
        <template #meta>
          <span class="status-pill status-pill--primary">当前 {{ foods.length }} 条菜品</span>
          <span class="status-pill status-pill--neutral">筛选后 {{ filteredFoods.length }} 条</span>
          <span v-if="selectedFileName" class="status-pill status-pill--success">
            最近导入：{{ selectedFileName }}
          </span>
        </template>

        <template #actions>
          <div class="button-row">
            <NButton type="primary" @click="openCreateModal">新增菜品</NButton>
            <NButton secondary @click="triggerUpload">导入文件</NButton>
            <NButton quaternary @click="loadFoods">刷新列表</NButton>
          </div>
        </template>
      </PageHeader>
    </AppCard>

    <section class="foods-stats">
      <StatCard label="菜品总数" :value="foods.length" hint="当前已进入推荐池的数据量。" />
      <StatCard label="平均价格" :value="`${priceStats} 元`" hint="只统计填写了价格的菜品。" />
      <StatCard label="主要分类" :value="topCategory" hint="当前菜品库中数量最多的分类。" />
    </section>

    <AppCard padding="md" class="foods-manager">
      <div class="foods-toolbar">
        <div class="foods-toolbar__filters">
          <NInput
            v-model:value="keyword"
            clearable
            placeholder="搜索菜名、店名、标签或备注"
          />
          <NSelect
            v-model:value="selectedCategory"
            clearable
            :options="categoryFilterOptions"
            placeholder="筛选分类"
          />
        </div>

        <div class="foods-toolbar__actions">
          <NButton type="primary" secondary @click="openCreateModal">新增菜品</NButton>
          <NButton quaternary @click="triggerUpload">重新导入</NButton>
          <NPopconfirm
            :disabled="!selectedFoodCount"
            @positive-click="handleBatchDeleteFoods"
          >
            <template #trigger>
              <NButton
                type="error"
                secondary
                :disabled="!selectedFoodCount"
                :loading="deletingFoods"
              >
                批量删除{{ selectedFoodCount ? ` ${selectedFoodCount}` : "" }}
              </NButton>
            </template>
            确认删除选中的 {{ selectedFoodCount }} 条菜品吗？
          </NPopconfirm>
        </div>
      </div>

      <NAlert v-if="uploadSummary" type="success" :show-icon="false">
        {{ uploadSummary }}
      </NAlert>

      <NAlert v-if="errorMessage" type="error" :show-icon="false">
        {{ errorMessage }}
      </NAlert>

      <div v-if="!loadingFoods && !filteredFoods.length" class="foods-empty">
        <NEmpty
          description="当前没有符合条件的菜品，试试新增一条或放宽搜索条件。"
        />
      </div>

      <div v-else class="food-table-wrap">
        <FoodTable
          v-model:checked-row-keys="selectedFoodIds"
          :foods="filteredFoods"
          :loading="loadingFoods"
          @edit="openEditModal"
          @delete="handleDeleteFood"
        />
      </div>
    </AppCard>

    <FoodFormModal
      :show="showFoodModal"
      :mode="modalMode"
      :food="activeFood"
      :saving="savingFood"
      @close="closeFoodModal"
      @submit="handleSubmitFood"
    />
  </div>
</template>

<style scoped>
.foods-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.foods-manager {
  display: grid;
  gap: 16px;
  min-width: 0;
  overflow: hidden;
}

.foods-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px;
  align-items: start;
}

.foods-toolbar__filters {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) minmax(180px, 260px);
  gap: 12px;
  min-width: 0;
}

.foods-toolbar__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.foods-empty {
  padding: 28px 0 12px;
}

.food-table-wrap {
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
}

.food-table-wrap :deep(.n-data-table) {
  min-width: 0;
}

.food-table-wrap :deep(.n-data-table-base-table-body) {
  overflow-x: auto;
}

@media (max-width: 980px) {
  .foods-stats {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1100px) {
  .foods-toolbar {
    grid-template-columns: 1fr;
  }

  .foods-toolbar__actions {
    justify-content: flex-start;
  }
}

@media (max-width: 720px) {
  .foods-toolbar__filters {
    grid-template-columns: 1fr;
  }

  .foods-toolbar__actions {
    display: grid;
  }

  .foods-toolbar__actions > * {
    width: 100%;
  }
}
</style>
