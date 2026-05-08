<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { NDatePicker, useMessage } from "naive-ui";

import AppCard from "@/components/AppCard.vue";
import EmptyState from "@/components/EmptyState.vue";
import PageHeader from "@/components/PageHeader.vue";
import StatCard from "@/components/StatCard.vue";
import {
  clearDailyRecords,
  listDailyRecords,
  updateDailyRecordActualChoice
} from "@/api/history";
import { emptyCopy, errorCopy } from "@/utils/copy";

defineOptions({
  name: "HistoryPage"
});

const router = useRouter();
const message = useMessage();

const loading = ref(false);
const clearing = ref(false);
const errorMessage = ref("");
const records = ref([]);
const savingActualChoiceId = ref(null);
const actualChoiceDrafts = reactive({});

const filters = reactive({
  dateRange: null,
  keyword: "",
  goal: "",
  milkTea: "all"
});

const hasDateFilter = computed(() => {
  return Array.isArray(filters.dateRange) && filters.dateRange.some(Boolean);
});

const goalOptions = computed(() => {
  const uniqueGoals = new Set();

  records.value.forEach((record) => {
    if (record.goal) {
      uniqueGoals.add(record.goal);
    }
  });

  return Array.from(uniqueGoals);
});

const filteredRecords = computed(() => {
  const keyword = filters.keyword.trim().toLowerCase();

  return records.value.filter((record) => {
    const matchesGoal = !filters.goal || record.goal === filters.goal;
    const matchesMilkTea =
      filters.milkTea === "all" ||
      (filters.milkTea === "had" && record.hadMilkTea) ||
      (filters.milkTea === "not-had" && !record.hadMilkTea);

    if (!matchesGoal || !matchesMilkTea) {
      return false;
    }

    if (!keyword) {
      return true;
    }

    const text = [
      record.summary,
      record.goal,
      record.taste,
      record.dislike,
      record.want,
      getActualChoice(record),
      ...(record.meals || []).flatMap((meal) => [meal.type, meal.name, meal.reason])
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return text.includes(keyword);
  });
});

const emptyState = computed(() => {
  if (hasDateFilter.value && !records.value.length) {
    return {
      badge: "日期范围无记录",
      title: emptyCopy.historyDateRangeTitle,
      description: emptyCopy.historyDateRangeDescription
    };
  }

  if (records.value.length) {
    return {
      badge: "暂无匹配结果",
      title: emptyCopy.historyFilteredTitle,
      description: emptyCopy.historyFilteredDescription
    };
  }

  return {
    badge: "暂无历史记录",
    title: emptyCopy.historyAllTitle,
    description: emptyCopy.historyAllDescription
  };
});

const stats = computed(() => {
  const total = records.value.length;
  const totalBudget = records.value.reduce(
    (sum, record) => sum + Number(record.budget || 0),
    0
  );
  const totalSpend = records.value.reduce(
    (sum, record) => sum + Number(record.totalPrice || 0),
    0
  );
  const hadMilkTeaCount = records.value.filter((record) => record.hadMilkTea).length;

  const goalCount = records.value.reduce((map, record) => {
    const key = record.goal || "无特殊目标";
    map[key] = (map[key] || 0) + 1;
    return map;
  }, {});

  let topGoal = "暂无数据";
  let topGoalCount = 0;

  Object.entries(goalCount).forEach(([goal, count]) => {
    if (count > topGoalCount) {
      topGoal = goal;
      topGoalCount = count;
    }
  });

  return {
    total,
    averageBudget: total ? (totalBudget / total).toFixed(1) : "0.0",
    averageSpend: total ? (totalSpend / total).toFixed(1) : "0.0",
    hadMilkTeaCount,
    topGoal
  };
});

function formatDate(value) {
  if (!value) {
    return "未知时间";
  }

  try {
    return new Intl.DateTimeFormat("zh-CN", {
      dateStyle: "medium",
      timeStyle: "short"
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function formatDateParam(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function formatCurrency(value) {
  return `${Number(value || 0).toFixed(1)} 元`;
}

function formatRecordTitle(record) {
  const names = (record.meals || [])
    .filter((meal) => Number(meal.rank || 1) === 1)
    .map((meal) => meal.name)
    .filter(Boolean);

  if (!names.length) {
    names.push(...(record.meals || []).map((meal) => meal.name).filter(Boolean).slice(0, 3));
  }

  return names.length ? names.join(" / ") : "今日推荐记录";
}

function getActualChoice(record) {
  return (
    record.actualChoice ||
    record.finalChoice ||
    record.selectedFood ||
    record.chosenFood ||
    ""
  );
}

function syncActualChoiceDrafts() {
  Object.keys(actualChoiceDrafts).forEach((key) => {
    delete actualChoiceDrafts[key];
  });

  records.value.forEach((record) => {
    actualChoiceDrafts[record.id] = getActualChoice(record);
  });
}

function getHistoryQueryOptions() {
  const [startDate, endDate] = Array.isArray(filters.dateRange)
    ? filters.dateRange
    : [];

  return {
    startDate: formatDateParam(startDate),
    endDate: formatDateParam(endDate)
  };
}

async function loadRecords() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const data = await listDailyRecords(getHistoryQueryOptions());
    records.value = Array.isArray(data?.data) ? data.data : [];
    syncActualChoiceDrafts();
  } catch (error) {
    errorMessage.value = error.message || errorCopy.historyLoad;
  } finally {
    loading.value = false;
  }
}

async function clearHistory() {
  if (!records.value.length) {
    return;
  }

  const confirmed = window.confirm("确认清空全部历史记录吗？这个操作无法撤销。");

  if (!confirmed) {
    return;
  }

  clearing.value = true;
  errorMessage.value = "";

  try {
    await clearDailyRecords();

    records.value = [];
    syncActualChoiceDrafts();
  } catch (error) {
    errorMessage.value = error.message || errorCopy.historyClear;
  } finally {
    clearing.value = false;
  }
}

function resetFilters() {
  filters.dateRange = null;
  filters.keyword = "";
  filters.goal = "";
  filters.milkTea = "all";
}

async function saveActualChoice(record) {
  savingActualChoiceId.value = record.id;
  errorMessage.value = "";

  try {
    const updatedRecord = await updateDailyRecordActualChoice(
      record.id,
      actualChoiceDrafts[record.id] || ""
    );
    const index = records.value.findIndex((item) => item.id === record.id);

    if (index >= 0) {
      records.value[index] = updatedRecord;
    }

    actualChoiceDrafts[record.id] = getActualChoice(updatedRecord);
    message.success("实际选择已保存。");
  } catch (error) {
    message.error(error.message || errorCopy.historyActualChoiceSave);
  } finally {
    savingActualChoiceId.value = null;
  }
}

function formatRecommendation(record) {
  const meals = record.meals || [];

  if (!meals.length) {
    return record.summary || "";
  }

  return meals
    .map((meal) => `${meal.type || "餐品"}：${meal.name || "暂无"}`)
    .join("；");
}

function toCsvCell(value) {
  const text = String(value ?? "").replace(/\r?\n/g, " ");
  return `"${text.replace(/"/g, '""')}"`;
}

function exportHistory() {
  const exportRecords = filteredRecords.value;

  if (!exportRecords.length) {
    message.warning("暂无可导出的历史记录。");
    return;
  }

  const rows = [
    [
      "日期",
      "预算",
      "口味偏好",
      "奶茶情况",
      "营养目标",
      "临时想吃",
      "推荐结果",
      "最终选择 / 实际选择"
    ],
    ...exportRecords.map((record) => [
      formatDate(record.createdAt),
      Number(record.budget || 0).toFixed(1),
      record.taste || "未填写",
      record.hadMilkTea ? "当天已喝奶茶" : "当天未喝奶茶",
      record.goal || "无特殊目标",
      record.want || "未填写",
      formatRecommendation(record),
      getActualChoice(record) || "暂无记录"
    ])
  ];

  const csv = `\ufeff${rows.map((row) => row.map(toCsvCell).join(",")).join("\n")}`;
  const blob = new Blob([csv], {
    type: "text/csv;charset=utf-8"
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const fileDate = formatDateParam(Date.now()).replaceAll("-", "");

  link.href = url;
  link.download = `to-eat-list-history-${fileDate}.csv`;
  link.click();
  URL.revokeObjectURL(url);
  message.success("已导出当前筛选结果。");
}

watch(
  () => filters.dateRange,
  () => {
    loadRecords();
  },
  { deep: true }
);

onMounted(() => {
  loadRecords();
});
</script>

<template>
  <div class="page history-page">
    <AppCard tone="accent" padding="lg">
      <PageHeader
        eyebrow="Recommendation Archive"
        title="历史记录页优先展示记录本身，而不是展示型大区块"
        description="每次生成推荐后，系统都会自动写入一条历史。这里保留标题、操作、统计和筛选，但会把真正的记录列表尽量提到首屏。"
        compact
      >
        <template #meta>
          <span class="status-pill status-pill--primary">共 {{ records.length }} 条历史</span>
          <span class="status-pill status-pill--neutral">
            当前筛选后 {{ filteredRecords.length }} 条
          </span>
        </template>

        <template #actions>
          <button class="button button--secondary" type="button" :disabled="loading" @click="loadRecords">
            {{ loading ? "刷新中..." : "刷新记录" }}
          </button>
          <button
            class="button button--secondary"
            type="button"
            :disabled="loading || !filteredRecords.length"
            @click="exportHistory"
          >
            导出 CSV
          </button>
          <button class="button button--ghost" type="button" @click="router.push('/recommend')">
            去生成推荐
          </button>
          <button
            class="button button--danger"
            type="button"
            :disabled="clearing || !records.length"
            @click="clearHistory"
          >
            {{ clearing ? "清空中..." : "清空历史" }}
          </button>
        </template>
      </PageHeader>
    </AppCard>

    <section class="history-stats">
      <StatCard label="累计推荐" :value="stats.total" hint="已经写入历史的推荐次数。" />
      <StatCard label="平均预算" :value="`${stats.averageBudget} 元`" hint="按历史记录中的预算字段计算。" />
      <StatCard label="平均花费" :value="`${stats.averageSpend} 元`" hint="按推荐结果中的总价估算。" />
      <StatCard label="最常见目标" :value="stats.topGoal" hint="当前历史中最常出现的饮食方向。" />
    </section>

    <AppCard class="filter-card" padding="md">
      <div class="filter-head">
        <div>
          <h2>筛选与搜索</h2>
          <p>按关键词、健康目标和奶茶状态快速定位记录。</p>
        </div>

        <button class="button button--ghost" type="button" @click="resetFilters">
          重置筛选
        </button>
      </div>

      <div class="filter-grid">
        <label class="field-label">
          <span>日期范围</span>
          <NDatePicker
            v-model:value="filters.dateRange"
            class="date-picker"
            type="daterange"
            clearable
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </label>

        <label class="field-label">
          <span>搜索关键词</span>
          <input
            v-model="filters.keyword"
            class="field-input"
            type="text"
            placeholder="搜索餐品、口味、总结或推荐理由"
          >
        </label>

        <label class="field-label">
          <span>健康目标</span>
          <select v-model="filters.goal" class="field-select">
            <option value="">全部目标</option>
            <option v-for="goal in goalOptions" :key="goal" :value="goal">
              {{ goal }}
            </option>
          </select>
        </label>

        <label class="field-label">
          <span>奶茶状态</span>
          <select v-model="filters.milkTea" class="field-select">
            <option value="all">全部</option>
            <option value="had">当天已喝奶茶</option>
            <option value="not-had">当天未喝奶茶</option>
          </select>
        </label>
      </div>
    </AppCard>

    <p v-if="errorMessage" class="history-error">{{ errorMessage }}</p>

    <AppCard v-if="loading && !records.length" padding="lg">
      <EmptyState
        badge="加载中"
        title="正在读取历史记录"
        description="稍等一下，系统正在把最近的推荐记录取回来。"
      />
    </AppCard>

    <AppCard v-else-if="!filteredRecords.length" padding="lg">
      <EmptyState
        :badge="emptyState.badge"
        :title="emptyState.title"
        :description="emptyState.description"
      >
        <template #actions>
          <button class="button button--primary" type="button" @click="router.push('/recommend')">
            去生成推荐
          </button>
        </template>
      </EmptyState>
    </AppCard>

    <section v-else class="record-list">
      <AppCard
        v-for="record in filteredRecords"
        :key="record.id"
        class="record-card"
        padding="md"
      >
        <div class="record-top">
          <div class="record-heading">
            <span class="record-time">{{ formatDate(record.createdAt) }}</span>
            <h2>{{ formatRecordTitle(record) }}</h2>
          </div>

          <div class="record-tags">
            <span class="status-pill status-pill--neutral">预算 {{ formatCurrency(record.budget) }}</span>
            <span class="status-pill status-pill--success">花费 {{ formatCurrency(record.totalPrice) }}</span>
            <span class="status-pill status-pill--warning">{{ record.goal || "无特殊目标" }}</span>
            <span class="status-pill status-pill--primary">
              最终选择：{{ getActualChoice(record) || "暂无记录" }}
            </span>
          </div>
        </div>

        <div class="record-meals">
          <article
            v-for="(meal, index) in record.meals || []"
            :key="`${record.id}-${meal.type}-${meal.rank || index}-${meal.name}`"
            class="meal-item"
          >
            <span>{{ meal.type }} {{ meal.rank || 1 }}</span>
            <strong>{{ meal.name }}</strong>
            <p
              v-if="
                meal.store ||
                meal.category ||
                (meal.price !== null && meal.price !== undefined)
              "
            >
              <template v-if="meal.store">{{ meal.store }}</template>
              <template v-if="meal.category"> · {{ meal.category }}</template>
              <template v-if="meal.price !== null && meal.price !== undefined">
                · {{ meal.price }} 元
              </template>
            </p>
            <details class="meal-detail">
              <summary>详情</summary>
              <p>{{ meal.reason }}</p>
            </details>
          </article>
        </div>

        <div class="record-meta">
          <span>口味偏好：{{ record.taste || "未填写" }}</span>
          <span>忌口：{{ record.dislike || "未填写" }}</span>
          <span>突然想吃：{{ record.want || "未填写" }}</span>
          <span>奶茶状态：{{ record.hadMilkTea ? "当天已喝奶茶" : "当天未喝奶茶" }}</span>
        </div>

        <div class="actual-choice-panel">
          <label class="field-label">
            <span>最终选择 / 实际选择</span>
            <input
              v-model="actualChoiceDrafts[record.id]"
              class="field-input"
              type="text"
              maxlength="240"
              placeholder="例如 最后点了香煎鸡胸饭"
            >
          </label>

          <button
            class="button button--secondary"
            type="button"
            :disabled="savingActualChoiceId === record.id"
            @click="saveActualChoice(record)"
          >
            {{ savingActualChoiceId === record.id ? "保存中..." : "保存实际选择" }}
          </button>
        </div>

        <details class="record-summary">
          <summary>查看推荐总结</summary>
          <p>{{ record.summary }}</p>
        </details>
      </AppCard>
    </section>
  </div>
</template>

<style scoped>
.history-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.filter-card {
  display: grid;
  gap: 16px;
}

.filter-head,
.record-top {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.filter-head h2,
.record-heading h2,
.meal-item strong {
  margin: 0;
}

.filter-head p,
.meal-item p,
.record-summary p {
  margin: 8px 0 0;
  color: var(--color-text-muted);
  line-height: 1.7;
}

.filter-grid {
  display: grid;
  grid-template-columns: 1.1fr 1.2fr 0.8fr 0.8fr;
  gap: 14px;
}

.date-picker {
  width: 100%;
}

.history-error {
  margin: 0;
  padding: 14px 16px;
  border: 1px solid rgba(185, 77, 63, 0.12);
  border-radius: var(--radius-md);
  color: var(--color-danger);
  background: rgba(185, 77, 63, 0.08);
  font-weight: 700;
}

.record-list {
  display: grid;
  gap: 14px;
}

.record-card {
  display: grid;
  gap: 16px;
}

.record-heading {
  display: grid;
  gap: 10px;
}

.record-time {
  display: inline-flex;
  width: fit-content;
  min-height: 32px;
  padding: 7px 11px;
  border-radius: 999px;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 900;
  background: rgba(17, 75, 95, 0.08);
}

.record-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.record-meals {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.meal-item {
  display: grid;
  align-content: start;
  gap: 10px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.72);
}

.meal-item span {
  display: inline-flex;
  min-height: 30px;
  padding: 6px 10px;
  border-radius: 999px;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 900;
  background: rgba(17, 75, 95, 0.08);
}

.meal-item strong {
  display: block;
  font-size: 18px;
  line-height: 1.25;
}

.meal-item p {
  margin: 0;
}

.meal-detail {
  padding-top: 8px;
  border-top: 1px solid rgba(17, 75, 95, 0.08);
}

.meal-detail summary {
  width: fit-content;
  cursor: pointer;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 800;
}

.record-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.record-meta span {
  padding: 9px 12px;
  border-radius: 14px;
  color: var(--color-text-muted);
  font-size: 14px;
  background: rgba(255, 255, 255, 0.66);
}

.actual-choice-panel {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: end;
  padding: 14px;
  border-radius: var(--radius-md);
  background: rgba(17, 75, 95, 0.05);
}

.record-summary {
  padding: 14px 16px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.6);
}

.record-summary summary {
  cursor: pointer;
  font-weight: 800;
}

@media (max-width: 1080px) {
  .history-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .filter-grid,
  .record-meals,
  .actual-choice-panel {
    grid-template-columns: 1fr;
  }

  .filter-head,
  .record-top {
    flex-direction: column;
  }

  .record-tags {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .history-stats {
    grid-template-columns: 1fr;
  }
}
</style>
