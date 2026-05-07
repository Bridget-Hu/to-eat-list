<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import AppCard from "@/components/AppCard.vue";
import EmptyState from "@/components/EmptyState.vue";
import PageHeader from "@/components/PageHeader.vue";
import StatCard from "@/components/StatCard.vue";
import { API_BASE, requestJson } from "@/utils/api";

defineOptions({
  name: "UploadPage"
});

const router = useRouter();

const fileInput = ref(null);
const selectedFile = ref(null);
const statusText = ref("请选择 txt / csv / json 文件");
const statusType = ref("neutral");
const loading = ref(false);
const foods = ref([]);
const loadingFoods = ref(false);
const clearingFoods = ref(false);
const imported = ref(false);
const importedCount = ref(0);
const errorMessage = ref("");
const keyword = ref("");

const filteredFoods = computed(() => {
  const search = keyword.value.trim().toLowerCase();

  if (!search) {
    return foods.value;
  }

  return foods.value.filter((food) => {
    const text = [food.name, food.category, food.taste, food.tags, food.note]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return text.includes(search);
  });
});

const categoryStats = computed(() => {
  const map = new Map();

  foods.value.forEach((food) => {
    const key = food.category || "未分类";
    map.set(key, (map.get(key) || 0) + 1);
  });

  return Array.from(map.entries()).sort((a, b) => b[1] - a[1]);
});

const averagePrice = computed(() => {
  const withPrice = foods.value.filter((food) => Number.isFinite(Number(food.price)));

  if (!withPrice.length) {
    return "0.0";
  }

  const total = withPrice.reduce((sum, food) => sum + Number(food.price || 0), 0);
  return (total / withPrice.length).toFixed(1);
});

const topCategory = computed(() => categoryStats.value[0]?.[0] ?? "暂无");

function formatCurrency(value) {
  return `${Number(value || 0).toFixed(1)} 元`;
}

function openFilePicker() {
  fileInput.value?.click();
}

async function loadFoods() {
  loadingFoods.value = true;
  errorMessage.value = "";

  try {
    const data = await requestJson("/foods");
    foods.value = Array.isArray(data?.data) ? data.data : [];
  } catch (error) {
    errorMessage.value = error.message || "获取菜品列表失败。";
  } finally {
    loadingFoods.value = false;
  }
}

async function handleFileChange(event) {
  const file = event.target.files?.[0];

  if (!file) {
    selectedFile.value = null;
    imported.value = false;
    importedCount.value = 0;
    statusText.value = "暂未选择文件";
    statusType.value = "neutral";
    return;
  }

  selectedFile.value = file;
  imported.value = false;
  importedCount.value = 0;
  loading.value = true;
  statusText.value = "正在解析并导入菜品数据...";
  statusType.value = "warning";
  errorMessage.value = "";

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE}/foods/upload`, {
      method: "POST",
      body: formData
    });

    let data = null;

    try {
      data = await response.json();
    } catch {
      data = null;
    }

    if (!response.ok) {
      throw new Error(data?.detail || data?.message || "导入失败，请检查文件格式。");
    }

    foods.value = Array.isArray(data?.data) ? data.data : [];
    imported.value = true;
    importedCount.value = data?.count ?? foods.value.length;
    statusText.value = `导入成功，当前菜品库共 ${importedCount.value} 条数据。`;
    statusType.value = "success";
  } catch (error) {
    imported.value = false;
    importedCount.value = 0;
    statusText.value = error.message || "导入失败，请确认后端服务已启动。";
    statusType.value = "danger";
  } finally {
    loading.value = false;
    event.target.value = "";
  }
}

async function clearFoods() {
  if (!foods.value.length) {
    return;
  }

  const confirmed = window.confirm("确认清空当前菜品库吗？这个操作无法撤销。");

  if (!confirmed) {
    return;
  }

  clearingFoods.value = true;
  errorMessage.value = "";

  try {
    await requestJson("/foods", {
      method: "DELETE"
    });

    foods.value = [];
    imported.value = false;
    importedCount.value = 0;
    keyword.value = "";
    statusText.value = "菜品库已清空。";
    statusType.value = "neutral";
  } catch (error) {
    errorMessage.value = error.message || "清空菜品库失败。";
  } finally {
    clearingFoods.value = false;
  }
}

onMounted(() => {
  loadFoods();
});
</script>

<template>
  <div class="page upload-page">
    <AppCard tone="accent" padding="lg">
      <PageHeader
        eyebrow="Food Source"
        title="导入页现在更像一个真正的数据管理页"
        description="这里保留原来的文件上传逻辑，同时补上菜品库查看、搜索和清空能力。你可以一边导入，一边确认当前有哪些菜品已经进入推荐系统。"
        compact
      >
        <template #meta>
          <span class="status-pill status-pill--primary">当前 {{ foods.length }} 条菜品</span>
          <span class="status-pill status-pill--neutral">支持 txt / csv / json</span>
        </template>

        <template #actions>
          <button class="button button--secondary" type="button" :disabled="loadingFoods" @click="loadFoods">
            {{ loadingFoods ? "刷新中..." : "刷新菜品库" }}
          </button>
          <button class="button button--ghost" type="button" @click="router.push('/recommend')">
            去生成推荐
          </button>
        </template>
      </PageHeader>
    </AppCard>

    <div class="upload-layout">
      <AppCard class="upload-panel" padding="lg">
        <input
          ref="fileInput"
          type="file"
          accept=".txt,.csv,.json"
          hidden
          @change="handleFileChange"
        >

        <div class="upload-dropzone">
          <div class="upload-dropzone__icon">TL</div>
          <div class="upload-dropzone__copy">
            <h2>导入外卖、食堂和常吃店铺的菜品</h2>
            <p>上传后会直接覆盖并重建当前菜品库，后续推荐都会基于这批数据生成。</p>
          </div>

          <div class="button-row">
            <button
              class="button button--primary"
              type="button"
              :disabled="loading"
              @click="openFilePicker"
            >
              {{ loading ? "导入中..." : selectedFile ? "重新选择文件" : "选择文件并导入" }}
            </button>
          </div>
        </div>

        <div class="upload-status">
          <div class="upload-status__row">
            <span class="upload-status__label">当前文件</span>
            <strong>{{ selectedFile ? selectedFile.name : "尚未选择文件" }}</strong>
          </div>

          <span class="status-pill" :class="`status-pill--${statusType}`">
            {{ statusText }}
          </span>
        </div>

        <div v-if="imported" class="upload-success">
          <strong>导入完成</strong>
          <p>当前菜品已经进入推荐池，可以直接去生成推荐，也可以继续检查下方菜品列表。</p>

          <div class="button-row">
            <button class="button button--ghost" type="button" @click="router.push('/')">
              返回首页
            </button>
            <button class="button button--secondary" type="button" @click="router.push('/recommend')">
              开始推荐
            </button>
          </div>
        </div>
      </AppCard>

      <div class="upload-side">
        <section class="upload-stats">
          <StatCard label="菜品总数" :value="foods.length" hint="当前已经进入推荐系统的数据量。" />
          <StatCard label="平均价格" :value="`${averagePrice} 元`" hint="只统计填写了价格的菜品。" />
          <StatCard label="主要分类" :value="topCategory" hint="当前菜品库里数量最多的分类。" />
        </section>

        <AppCard class="guide-card" padding="md" tone="muted">
          <h2>整理建议</h2>

          <div class="guide-list">
            <article class="guide-item">
              <strong>价格和分类尽量补齐</strong>
              <p>这样推荐阶段才能更稳定地控制预算，并区分早餐、午餐和晚餐。</p>
            </article>

            <article class="guide-item">
              <strong>标签写得具体一些</strong>
              <p>像“清淡”“微辣”“高蛋白”“轻食”这类关键词，会直接影响匹配结果。</p>
            </article>

            <article class="guide-item">
              <strong>备注保留真实体验</strong>
              <p>例如“适合赶时间”“容易腻”“减脂友好”，会让推荐更像你自己的判断。</p>
            </article>
          </div>
        </AppCard>
      </div>
    </div>

    <AppCard class="food-library" padding="lg">
      <div class="library-head">
        <div>
          <h2>菜品库</h2>
          <p>可以先按关键词确认导入结果，再决定是否继续补充或清空重来。</p>
        </div>

        <div class="button-row">
          <button
            class="button button--danger"
            type="button"
            :disabled="clearingFoods || !foods.length"
            @click="clearFoods"
          >
            {{ clearingFoods ? "清空中..." : "清空菜品库" }}
          </button>
        </div>
      </div>

      <div class="library-toolbar">
        <label class="field-label">
          <span>搜索菜品</span>
          <input
            v-model="keyword"
            class="field-input"
            type="text"
            placeholder="搜索菜名、分类、口味、标签或备注"
          >
        </label>

        <div class="library-tags">
          <span
            v-for="[name, count] in categoryStats.slice(0, 4)"
            :key="name"
            class="status-pill status-pill--neutral"
          >
            {{ name }} {{ count }}
          </span>
        </div>
      </div>

      <p v-if="errorMessage" class="library-error">{{ errorMessage }}</p>

      <div v-if="loadingFoods && !foods.length" class="library-loading">
        <EmptyState
          badge="加载中"
          title="正在读取当前菜品库"
          description="稍等一下，系统正在同步已经导入的菜品数据。"
        />
      </div>

      <div v-else-if="!filteredFoods.length" class="library-empty">
        <EmptyState
          :badge="foods.length ? '暂无匹配结果' : '菜品库为空'"
          :title="foods.length ? '没有找到符合搜索条件的菜品' : '还没有导入任何菜品'"
          :description="foods.length ? '可以换个关键词继续搜，或者直接查看全部菜品。' : '先选择文件导入，推荐页才会有可用数据。'"
        >
          <template #actions>
            <button class="button button--primary" type="button" @click="openFilePicker">
              立即导入菜品
            </button>
          </template>
        </EmptyState>
      </div>

      <div v-else class="table-shell">
        <table class="food-table">
          <thead>
            <tr>
              <th>菜品</th>
              <th>分类</th>
              <th>价格</th>
              <th>口味 / 标签</th>
              <th>备注</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="food in filteredFoods" :key="food.id">
              <td>
                <div class="food-name">
                  <strong>{{ food.name }}</strong>
                  <span>{{ food.id }}</span>
                </div>
              </td>
              <td>{{ food.category || "未分类" }}</td>
              <td>{{ formatCurrency(food.price) }}</td>
              <td>
                <div class="food-tags-cell">
                  <span>{{ food.taste || "未填写口味" }}</span>
                  <span>{{ food.tags || "未填写标签" }}</span>
                </div>
              </td>
              <td>{{ food.note || "无备注" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </AppCard>
  </div>
</template>

<style scoped>
.upload-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(280px, 0.92fr);
  gap: 18px;
  align-items: start;
}

.upload-panel,
.guide-card,
.food-library {
  display: grid;
  gap: 18px;
}

.upload-dropzone {
  display: grid;
  justify-items: start;
  gap: 18px;
  padding: 24px;
  border: 1px dashed rgba(17, 75, 95, 0.22);
  border-radius: var(--radius-lg);
  background:
    radial-gradient(circle at top, rgba(240, 154, 74, 0.12), transparent 58%),
    rgba(255, 255, 255, 0.7);
}

.upload-dropzone__icon {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  border-radius: 18px;
  color: #fff;
  font-weight: 900;
  background: linear-gradient(135deg, var(--color-accent), #ffba76);
  box-shadow: 0 16px 28px rgba(240, 154, 74, 0.22);
}

.upload-dropzone__copy h2,
.guide-card h2,
.library-head h2 {
  margin: 0;
}

.upload-dropzone__copy p,
.guide-item p,
.library-head p {
  margin: 8px 0 0;
  color: var(--color-text-muted);
  line-height: 1.7;
}

.upload-status {
  display: grid;
  gap: 12px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.68);
}

.upload-status__row {
  display: grid;
  gap: 6px;
}

.upload-status__label {
  color: var(--color-text-muted);
  font-size: 13px;
}

.upload-success {
  display: grid;
  gap: 10px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: rgba(36, 118, 95, 0.08);
}

.upload-success strong {
  font-size: 18px;
}

.upload-success p,
.guide-item p {
  margin: 0;
}

.upload-side {
  display: grid;
  gap: 18px;
}

.upload-stats {
  display: grid;
  gap: 14px;
}

.guide-list {
  display: grid;
  gap: 12px;
}

.guide-item {
  display: grid;
  gap: 8px;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.58);
}

.library-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.library-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px;
  align-items: end;
}

.library-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.library-error {
  margin: 0;
  padding: 14px 16px;
  border: 1px solid rgba(185, 77, 63, 0.12);
  border-radius: var(--radius-md);
  color: var(--color-danger);
  background: rgba(185, 77, 63, 0.08);
  font-weight: 700;
}

.table-shell {
  overflow-x: auto;
}

.food-table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
}

.food-table th,
.food-table td {
  padding: 14px 12px;
  text-align: left;
  vertical-align: top;
  border-bottom: 1px solid rgba(17, 75, 95, 0.08);
}

.food-table th {
  color: var(--color-text-muted);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.food-name {
  display: grid;
  gap: 6px;
}

.food-name strong {
  font-size: 16px;
}

.food-name span {
  color: var(--color-text-muted);
  font-size: 12px;
}

.food-tags-cell {
  display: grid;
  gap: 8px;
}

.food-tags-cell span {
  display: inline-flex;
  width: fit-content;
  min-height: 30px;
  padding: 6px 10px;
  border-radius: 999px;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 800;
  background: rgba(17, 75, 95, 0.08);
}

@media (max-width: 980px) {
  .upload-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .library-head,
  .library-toolbar {
    grid-template-columns: 1fr;
    display: grid;
  }

  .library-tags {
    justify-content: flex-start;
  }
}
</style>
