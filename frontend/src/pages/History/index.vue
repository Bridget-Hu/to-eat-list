<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import AppCard from "@/components/AppCard.vue";
import EmptyState from "@/components/EmptyState.vue";
import PageHeader from "@/components/PageHeader.vue";
import StatCard from "@/components/StatCard.vue";
import { requestJson } from "@/utils/api";

defineOptions({
  name: "HistoryPage"
});

const router = useRouter();

const loading = ref(false);
const clearing = ref(false);
const errorMessage = ref("");
const records = ref([]);

const filters = reactive({
  keyword: "",
  goal: "",
  milkTea: "all"
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
      ...(record.meals || []).flatMap((meal) => [meal.type, meal.name, meal.reason])
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return text.includes(keyword);
  });
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

function formatCurrency(value) {
  return `${Number(value || 0).toFixed(1)} 元`;
}

function formatRecordTitle(record) {
  const names = (record.meals || []).map((meal) => meal.name).filter(Boolean);
  return names.length ? names.join(" / ") : "今日推荐记录";
}

async function loadRecords() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const data = await requestJson("/daily-records");
    records.value = Array.isArray(data?.data) ? data.data : [];
  } catch (error) {
    errorMessage.value = error.message || "获取历史记录失败。";
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
    await requestJson("/daily-records", {
      method: "DELETE"
    });

    records.value = [];
  } catch (error) {
    errorMessage.value = error.message || "清空历史记录失败。";
  } finally {
    clearing.value = false;
  }
}

function resetFilters() {
  filters.keyword = "";
  filters.goal = "";
  filters.milkTea = "all";
}

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
        :badge="records.length ? '暂无匹配结果' : '暂无历史记录'"
        :title="records.length ? '当前筛选条件下没有匹配记录' : '还没有可展示的历史记录'"
        :description="records.length ? '可以放宽筛选条件，或者直接搜索更少的关键词。' : '先去生成一条推荐，历史页就会自动沉淀真实数据。'"
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
          </div>
        </div>

        <div class="record-meals">
          <article
            v-for="meal in record.meals || []"
            :key="`${record.id}-${meal.type}`"
            class="meal-item"
          >
            <span>{{ meal.type }}</span>
            <strong>{{ meal.name }}</strong>
            <p>{{ meal.reason }}</p>
          </article>
        </div>

        <div class="record-meta">
          <span>口味偏好：{{ record.taste || "未填写" }}</span>
          <span>忌口：{{ record.dislike || "未填写" }}</span>
          <span>突然想吃：{{ record.want || "未填写" }}</span>
          <span>奶茶状态：{{ record.hadMilkTea ? "当天已喝奶茶" : "当天未喝奶茶" }}</span>
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
  grid-template-columns: 1.4fr 0.8fr 0.8fr;
  gap: 14px;
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
  margin-top: 12px;
  font-size: 18px;
  line-height: 1.25;
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
  .record-meals {
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
