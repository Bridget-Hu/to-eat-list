<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";

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
    <section class="panel hero-panel">
      <div>
        <p class="section-kicker">Recommendation Archive</p>
        <h1 class="section-title">历史记录页现在接入了真实推荐结果。</h1>
        <p class="section-desc">
          每次生成推荐后，系统都会自动写入一条历史。你可以在这里回看最近吃了什么、预算控制得如何，以及哪些偏好出现得最多。
        </p>
      </div>

      <div class="hero-actions">
        <button class="secondary-button" type="button" :disabled="loading" @click="loadRecords">
          {{ loading ? "刷新中..." : "刷新记录" }}
        </button>

        <button class="ghost-button" type="button" @click="router.push('/recommend')">
          去生成新的推荐
        </button>

        <button
          class="ghost-button danger-button"
          type="button"
          :disabled="clearing || !records.length"
          @click="clearHistory"
        >
          {{ clearing ? "清空中..." : "清空历史" }}
        </button>
      </div>
    </section>

    <section class="stats-grid">
      <article class="panel stat-card">
        <span>累计推荐</span>
        <strong>{{ stats.total }}</strong>
        <p>已写入历史的推荐次数</p>
      </article>

      <article class="panel stat-card">
        <span>平均预算</span>
        <strong>{{ stats.averageBudget }} 元</strong>
        <p>按历史记录中的预算字段计算</p>
      </article>

      <article class="panel stat-card">
        <span>平均花费</span>
        <strong>{{ stats.averageSpend }} 元</strong>
        <p>按推荐结果中的预计总价计算</p>
      </article>

      <article class="panel stat-card">
        <span>最常见目标</span>
        <strong>{{ stats.topGoal }}</strong>
        <p>当前最常出现的饮食方向</p>
      </article>
    </section>

    <section class="panel filter-panel">
      <div class="filter-header">
        <div>
          <h2>筛选与搜索</h2>
          <p>支持按关键词、目标和奶茶摄入状态快速回看记录。</p>
        </div>

        <button class="ghost-button" type="button" @click="resetFilters">重置筛选</button>
      </div>

      <div class="filter-grid">
        <label class="field-label">
          搜索关键词
          <input
            v-model="filters.keyword"
            class="field-input"
            type="text"
            placeholder="搜索餐品、口味、总结或推荐理由"
          >
        </label>

        <label class="field-label">
          健康目标
          <select v-model="filters.goal" class="field-select">
            <option value="">全部目标</option>
            <option v-for="goal in goalOptions" :key="goal" :value="goal">
              {{ goal }}
            </option>
          </select>
        </label>

        <label class="field-label">
          奶茶状态
          <select v-model="filters.milkTea" class="field-select">
            <option value="all">全部</option>
            <option value="had">当天已喝奶茶</option>
            <option value="not-had">当天未喝奶茶</option>
          </select>
        </label>
      </div>
    </section>

    <p v-if="errorMessage" class="panel error-banner">{{ errorMessage }}</p>

    <section v-if="!loading && !filteredRecords.length" class="panel empty-panel">
      <h2>还没有可展示的历史记录</h2>
      <p>
        {{ records.length ? "当前筛选条件下没有匹配结果，试试放宽条件。" : "先去生成一条推荐，历史页就会自动出现真实数据。" }}
      </p>

      <button class="primary-button" type="button" @click="router.push('/recommend')">
        去生成推荐
      </button>
    </section>

    <section v-else class="record-list">
      <article
        v-for="record in filteredRecords"
        :key="record.id"
        class="panel record-card"
      >
        <div class="record-top">
          <div>
            <span class="record-time">{{ formatDate(record.createdAt) }}</span>
            <h2>
              {{ (record.meals || []).map((meal) => meal.name).filter(Boolean).join(" · ") }}
            </h2>
          </div>

          <div class="record-tags">
            <span class="status-pill neutral">预算 {{ formatCurrency(record.budget) }}</span>
            <span class="status-pill success">预计花费 {{ formatCurrency(record.totalPrice) }}</span>
            <span class="status-pill warning">
              {{ record.goal || "无特殊目标" }}
            </span>
          </div>
        </div>

        <div class="meal-grid">
          <article
            v-for="meal in record.meals || []"
            :key="`${record.id}-${meal.type}`"
            class="meal-card"
          >
            <span>{{ meal.type }}</span>
            <strong>{{ meal.name }}</strong>
            <p>{{ meal.reason }}</p>
          </article>
        </div>

        <div class="meta-row">
          <span>口味偏好：{{ record.taste || "未填写" }}</span>
          <span>忌口：{{ record.dislike || "未填写" }}</span>
          <span>突然想吃：{{ record.want || "未填写" }}</span>
          <span>奶茶状态：{{ record.hadMilkTea ? "当天已喝奶茶" : "当天未喝奶茶" }}</span>
        </div>

        <details class="summary-box">
          <summary>查看推荐总结</summary>
          <p>{{ record.summary }}</p>
        </details>
      </article>
    </section>
  </div>
</template>

<style scoped>
.hero-panel,
.filter-panel,
.empty-panel,
.record-card {
  padding: 28px;
}

.hero-panel,
.filter-header,
.record-top {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
}

.hero-actions,
.record-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.danger-button {
  color: var(--danger);
  box-shadow: inset 0 0 0 1px rgba(196, 69, 54, 0.12);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  padding: 22px;
}

.stat-card span {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.stat-card strong {
  display: block;
  margin-top: 12px;
  font-size: 30px;
  line-height: 1.1;
}

.stat-card p,
.filter-header p,
.meal-card p,
.summary-box p,
.empty-panel p {
  margin: 10px 0 0;
  color: var(--text-secondary);
  line-height: 1.75;
}

.filter-header h2,
.record-top h2,
.empty-panel h2,
.meal-card strong {
  margin: 0;
}

.filter-grid {
  display: grid;
  grid-template-columns: 1.4fr 0.8fr 0.8fr;
  gap: 16px;
  margin-top: 22px;
}

.error-banner {
  margin: 0;
  padding: 16px 20px;
  color: var(--danger);
  font-weight: 800;
}

.empty-panel {
  display: grid;
  justify-items: start;
  gap: 14px;
}

.record-list {
  display: grid;
  gap: 16px;
}

.record-time {
  display: inline-flex;
  margin-bottom: 10px;
  padding: 8px 12px;
  border-radius: 999px;
  color: var(--accent-primary);
  font-size: 13px;
  font-weight: 900;
  background: rgba(17, 75, 95, 0.08);
}

.meal-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 18px;
}

.meal-card {
  padding: 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.74);
}

.meal-card span {
  display: inline-flex;
  margin-bottom: 12px;
  padding: 7px 11px;
  border-radius: 999px;
  color: var(--accent-primary);
  font-size: 12px;
  font-weight: 900;
  background: rgba(17, 75, 95, 0.08);
}

.meal-card strong {
  display: block;
  font-size: 20px;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}

.meta-row span {
  padding: 10px 14px;
  border-radius: 14px;
  color: var(--text-secondary);
  font-size: 14px;
  background: rgba(255, 255, 255, 0.64);
}

.summary-box {
  margin-top: 16px;
  padding: 16px 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.64);
}

.summary-box summary {
  cursor: pointer;
  font-weight: 800;
}

@media (max-width: 1080px) {
  .stats-grid,
  .filter-grid,
  .meal-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 860px) {
  .hero-panel,
  .filter-header,
  .record-top {
    flex-direction: column;
  }

  .hero-actions,
  .record-tags {
    justify-content: flex-start;
  }

  .filter-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hero-panel,
  .filter-panel,
  .empty-panel,
  .record-card {
    padding: 22px;
  }

  .stats-grid,
  .meal-grid {
    grid-template-columns: 1fr;
  }
}
</style>
