<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { storeToRefs } from "pinia";
import { useRouter } from "vue-router";
import { useMessage } from "naive-ui";

import AppCard from "@/components/AppCard.vue";
import EmptyState from "@/components/EmptyState.vue";
import PageHeader from "@/components/PageHeader.vue";
import {
  getLatestUserPreference,
  saveUserPreference
} from "@/api/userPreferences";
import { useSavedConditionsStore } from "@/stores/savedConditions";
import { requestJson } from "@/utils/api";
import { emptyCopy, errorCopy } from "@/utils/copy";

defineOptions({
  name: "RecommendPage"
});

const router = useRouter();
const message = useMessage();
const savedConditionsStore = useSavedConditionsStore();
const { conditions: savedConditions, count: savedConditionCount } =
  storeToRefs(savedConditionsStore);

const form = reactive({
  budget: 60,
  taste: "",
  dislike: "",
  want: "",
  goal: "",
  hadMilkTea: false
});

const result = ref(null);
const loading = ref(false);
const errorMessage = ref("");
const savingPreference = ref(false);
const loadingPreference = ref(false);
const lastSavedAt = ref("");
const savedConditionName = ref("");
const selectedConditionId = ref("");

const healthGoalOptions = [
  { label: "无特殊目标", value: "" },
  { label: "控制预算", value: "控制预算" },
  { label: "吃得清淡", value: "吃得清淡" },
  { label: "高蛋白", value: "高蛋白" },
  { label: "低脂", value: "低脂" },
  { label: "多蔬菜", value: "多蔬菜" },
  { label: "少糖", value: "少糖" },
  { label: "少油", value: "少油" },
  { label: "吃饱一点", value: "吃饱一点" },
  { label: "避免奶茶", value: "避免奶茶" },
  { label: "适合赶时间", value: "适合赶时间" }
];

const mealCards = computed(() => {
  if (!result.value) {
    return [];
  }

  if (Array.isArray(result.value.meals) && result.value.meals.length > 0) {
    return result.value.meals.map((meal) => ({
      type: meal.type,
      name: meal.name,
      reason: meal.reason,
      rank: Number(meal.rank || 1),
      reasons: meal.reasons || [],
      score: meal.score,
      price: meal.price,
      store: meal.store,
      category: meal.category
    }));
  }

  return [
    {
      type: "早餐",
      name: result.value.breakfast,
      reason: result.value.breakfastReason,
      rank: 1,
      reasons: []
    },
    {
      type: "午餐",
      name: result.value.lunch,
      reason: result.value.lunchReason,
      rank: 1,
      reasons: []
    },
    {
      type: "晚餐",
      name: result.value.dinner,
      reason: result.value.dinnerReason,
      rank: 1,
      reasons: []
    }
  ];
});

const hasRecommendationResult = computed(() => {
  if (!result.value) {
    return false;
  }

  if (Array.isArray(result.value.recommendations)) {
    return result.value.recommendations.length > 0;
  }

  return mealCards.value.some((meal) => !String(meal.name || "").startsWith("暂无"));
});

const tips = [
  {
    title: "预算给范围就够",
    desc: "不需要精确到整数，系统会优先找更贴近预算的组合。"
  },
  {
    title: "口味和突然想吃分开填",
    desc: "前者描述长期偏好，后者描述今天的即时情绪。"
  },
  {
    title: "忌口支持多个关键词",
    desc: "可以用空格、顿号或逗号分隔，后端会逐项匹配。"
  }
];

function clearForm() {
  form.budget = 60;
  form.taste = "";
  form.dislike = "";
  form.want = "";
  form.goal = "";
  form.hadMilkTea = false;
  result.value = null;
  errorMessage.value = "";
  selectedConditionId.value = "";
}

function formatDateTime(value) {
  if (!value) {
    return "";
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

function applyFormValues(values = {}) {
  form.budget = Number(values.budget ?? 60);
  form.taste = values.taste || "";
  form.dislike = values.dislike || "";
  form.want = values.want || "";
  form.goal = values.goal || "";
  form.hadMilkTea = Boolean(values.hadMilkTea);
}

function applyPreference(preference) {
  applyFormValues(preference);
  lastSavedAt.value = formatDateTime(preference.updatedAt || preference.createdAt);
}

function snapshotForm() {
  return {
    budget: form.budget,
    taste: form.taste,
    dislike: form.dislike,
    want: form.want,
    goal: form.goal,
    hadMilkTea: form.hadMilkTea
  };
}

function applySavedCondition(condition) {
  applyFormValues(condition.form);
  selectedConditionId.value = condition.id;
  result.value = null;
  errorMessage.value = "";
  message.success(`已填入“${condition.name}”`);
}

function saveCurrentCondition() {
  const name = savedConditionName.value.trim();

  if (!name) {
    message.warning("请先填写常用条件名称。");
    return;
  }

  const saved = savedConditionsStore.saveCondition(name, snapshotForm());

  if (!saved) {
    message.error(savedConditionsStore.storageError || errorCopy.savedConditionsWrite);
    return;
  }

  selectedConditionId.value = saved.id;
  savedConditionName.value = "";
  message.success("常用条件已保存。");
}

function deleteSavedCondition(condition) {
  const deleted = savedConditionsStore.deleteCondition(condition.id);

  if (!deleted) {
    message.error(savedConditionsStore.storageError || errorCopy.savedConditionsWrite);
    return;
  }

  if (selectedConditionId.value === condition.id) {
    selectedConditionId.value = "";
  }

  message.success(`已删除“${condition.name}”。`);
}

async function loadLatestPreference() {
  loadingPreference.value = true;

  try {
    const latestPreference = await getLatestUserPreference();
    applyPreference(latestPreference);
  } catch (error) {
    if (!String(error.message || "").includes("还没有保存过用户偏好")) {
      message.error(error.message || errorCopy.preferenceLoad);
    }
  } finally {
    loadingPreference.value = false;
  }
}

async function submitPreference() {
  savingPreference.value = true;

  try {
    const savedPreference = await saveUserPreference({ ...form });
    applyPreference(savedPreference);
    message.success("偏好已保存，下次打开会自动回显最近一次记录");
  } catch (error) {
    message.error(error.message || errorCopy.preferenceSave);
  } finally {
    savingPreference.value = false;
  }
}

async function generateRecommend() {
  loading.value = true;
  errorMessage.value = "";
  result.value = null;

  try {
    result.value = await requestJson("/recommend/daily", {
      method: "POST",
      body: JSON.stringify(form)
    });
  } catch (error) {
    errorMessage.value = error.message || errorCopy.recommendationGenerate;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  savedConditionsStore.loadConditions();

  if (savedConditionsStore.storageError) {
    message.warning(savedConditionsStore.storageError);
  }

  loadLatestPreference();
});
</script>

<template>
  <div class="page recommend-page">
    <AppCard tone="accent" padding="lg">
      <PageHeader
        eyebrow="Recommendation Flow"
        title="先填条件，再在同一屏里查看今天的推荐结果"
        description="这一页现在按工具页来组织。左侧专注输入预算、口味、忌口和目标，右侧即时承接推荐结果、空状态和输入建议，减少来回滚动。"
        compact
      >
        <template #meta>
          <span class="status-pill status-pill--primary">生成后自动写入历史</span>
          <span class="status-pill status-pill--neutral">建议先导入完整菜品库</span>
          <span v-if="lastSavedAt" class="status-pill status-pill--success">
            最近保存：{{ lastSavedAt }}
          </span>
          <span v-else-if="loadingPreference" class="status-pill status-pill--neutral">
            正在读取最近一次偏好
          </span>
        </template>

        <template #actions>
          <button
            class="button button--ghost"
            type="button"
            @click="router.push('/upload')"
          >
            导入菜品
          </button>
          <button
            class="button button--secondary"
            type="button"
            @click="router.push('/history')"
          >
            查看历史
          </button>
        </template>
      </PageHeader>
    </AppCard>

    <div class="recommend-layout">
      <AppCard class="form-card" padding="lg">
        <div class="section-head">
          <div>
            <h2>推荐条件</h2>
            <p>信息越贴近今天的真实状态，结果就越像你自己会选出来的那份菜单。</p>
          </div>

          <button class="button button--ghost" type="button" @click="clearForm">
            清空条件
          </button>
        </div>

        <div class="form-grid">
          <label class="field-label">
            <span>今日预算 / 元</span>
            <input
              v-model.number="form.budget"
              class="field-input"
              type="number"
              min="0"
              placeholder="例如 60"
            >
          </label>

          <label class="field-label">
            <span>健康目标</span>
            <select v-model="form.goal" class="field-select">
              <option
                v-for="option in healthGoalOptions"
                :key="option.value || 'none'"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </label>

          <label class="field-label">
            <span>口味偏好</span>
            <input
              v-model="form.taste"
              class="field-input"
              type="text"
              placeholder="例如 清淡、微辣、咸香"
            >
          </label>

          <label class="field-label">
            <span>忌口关键词</span>
            <input
              v-model="form.dislike"
              class="field-input"
              type="text"
              placeholder="例如 香菜、肥肉、海鲜"
            >
          </label>

          <label class="field-label form-grid__full">
            <span>今天突然很想吃</span>
            <input
              v-model="form.want"
              class="field-input"
              type="text"
              placeholder="例如 牛肉、米饭、面、轻食"
            >
          </label>

          <label class="milk-tea-toggle form-grid__full">
            <input v-model="form.hadMilkTea" type="checkbox">
            <div>
              <strong>今天已经喝过奶茶</strong>
              <p>推荐时尽量回避高糖饮品，优先更轻的搭配。</p>
            </div>
          </label>
        </div>

        <section class="saved-conditions">
          <div class="saved-conditions__head">
            <div>
              <h3>常用条件</h3>
              <p>把常填的预算、口味和目标保存下来，下次一键填入。</p>
            </div>

            <span class="status-pill status-pill--neutral">
              {{ savedConditionCount }} 个模板
            </span>
          </div>

          <div class="save-condition-row">
            <label class="field-label">
              <span>条件名称</span>
              <input
                v-model="savedConditionName"
                class="field-input"
                type="text"
                maxlength="24"
                placeholder="例如 工作日午餐"
              >
            </label>

            <button
              class="button button--secondary"
              type="button"
              @click="saveCurrentCondition"
            >
              保存为常用条件
            </button>
          </div>

          <div v-if="!savedConditions.length" class="saved-conditions__empty">
            <strong>{{ emptyCopy.savedConditionsTitle }}</strong>
            <p>{{ emptyCopy.savedConditionsDescription }}</p>
          </div>

          <div v-else class="saved-condition-list">
            <article
              v-for="condition in savedConditions"
              :key="condition.id"
              class="saved-condition-item"
              :class="{ 'saved-condition-item--active': selectedConditionId === condition.id }"
            >
              <div>
                <strong>{{ condition.name }}</strong>
                <span>{{ formatDateTime(condition.updatedAt) || "刚刚保存" }}</span>
              </div>

              <div class="saved-condition-actions">
                <button
                  class="button button--ghost"
                  type="button"
                  @click="applySavedCondition(condition)"
                >
                  填入
                </button>
                <button
                  class="button button--danger"
                  type="button"
                  @click="deleteSavedCondition(condition)"
                >
                  删除
                </button>
              </div>
            </article>
          </div>
        </section>

        <div class="form-footer">
          <div class="button-row">
            <button
              class="button button--secondary"
              type="button"
              :disabled="savingPreference"
              @click="submitPreference"
            >
              {{ savingPreference ? "保存中..." : "保存今日偏好" }}
            </button>
            <button
              class="button button--primary"
              type="button"
              :disabled="loading"
              @click="generateRecommend"
            >
              {{ loading ? "生成中..." : "生成今日推荐" }}
            </button>
          </div>

          <span class="status-pill status-pill--neutral">推荐完成后会自动保存到历史记录</span>
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      </AppCard>

      <div class="result-column">
        <AppCard class="result-card" padding="lg">
          <div v-if="loading" class="result-loading">
            <span class="status-pill status-pill--primary">正在生成</span>
            <h2>正在根据你今天的条件匹配菜单</h2>
            <p>预算、口味、忌口和健康目标都会一起参与筛选。</p>
          </div>

          <template v-else-if="result && !hasRecommendationResult">
            <EmptyState
              badge="暂无结果"
              title="暂无符合条件的菜品"
              description="可以尝试放宽预算、减少忌口，或先导入更多菜品。"
            >
              <template #actions>
                <button
                  class="button button--ghost"
                  type="button"
                  @click="router.push('/upload')"
                >
                  去导入菜品
                </button>
              </template>
            </EmptyState>
          </template>

          <template v-else-if="result">
            <div class="section-head result-head">
              <div>
                <h2>今日推荐结果</h2>
                <p>生成成功后会自动写入历史记录，方便后续回看。</p>
              </div>

              <div class="result-metrics">
                <span class="status-pill status-pill--success">
                  预计总价 {{ result.totalPrice ?? 0 }} 元
                </span>
                <span class="status-pill status-pill--neutral">
                  预算剩余 {{ result.remainingBudget ?? 0 }} 元
                </span>
              </div>
            </div>

            <div class="meal-grid">
              <article
                v-for="meal in mealCards"
                :key="`${meal.type}-${meal.rank}-${meal.name}`"
                class="meal-item"
              >
                <div class="meal-item__meta">
                  <span>{{ meal.type }} {{ meal.rank }}</span>
                  <strong v-if="meal.score !== null && meal.score !== undefined">
                    评分 {{ meal.score }}
                  </strong>
                </div>
                <h3>{{ meal.name }}</h3>
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
                  <summary>查看详情</summary>
                  <ul v-if="meal.reasons?.length" class="reason-list">
                    <li v-for="reason in meal.reasons" :key="`${meal.type}-${reason}`">
                      {{ reason }}
                    </li>
                  </ul>
                  <p v-else>{{ meal.reason }}</p>
                </details>
              </article>
            </div>

            <div class="result-summary">
              <h3>推荐总结</h3>
              <p>{{ result.summary }}</p>

              <div class="button-row">
                <button
                  class="button button--secondary"
                  type="button"
                  @click="router.push('/history')"
                >
                  去历史页查看
                </button>
              </div>
            </div>
          </template>

          <EmptyState
            v-else
            badge="等待生成"
            title="先填写左侧条件，再生成今天的推荐"
            description="推荐页首屏现在直接放出主要表单。你可以先从预算和目标开始填，剩下的偏好条件按需补充。"
          >
            <template #actions>
              <button
                class="button button--ghost"
                type="button"
                @click="router.push('/upload')"
              >
                还没导入菜品？
              </button>
            </template>
          </EmptyState>
        </AppCard>

        <AppCard class="tips-card" padding="md" tone="muted">
          <h2>输入建议</h2>

          <div class="tip-list">
            <article v-for="item in tips" :key="item.title" class="tip-item">
              <strong>{{ item.title }}</strong>
              <p>{{ item.desc }}</p>
            </article>
          </div>
        </AppCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
.recommend-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.02fr) minmax(320px, 0.98fr);
  gap: 18px;
  align-items: start;
}

.form-card,
.result-card,
.tips-card {
  display: grid;
  gap: 18px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.section-head h2,
.meal-item h3,
.result-summary h3,
.tips-card h2,
.result-loading h2 {
  margin: 0;
}

.section-head p,
.result-summary p,
.tip-item p,
.result-loading p {
  margin: 8px 0 0;
  color: var(--color-text-muted);
  line-height: 1.7;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.form-grid__full {
  grid-column: 1 / -1;
}

.saved-conditions {
  display: grid;
  gap: 14px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.54);
}

.saved-conditions__head,
.save-condition-row,
.saved-condition-item {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
}

.saved-conditions__head h3,
.saved-conditions__empty strong,
.saved-condition-item strong {
  margin: 0;
}

.saved-conditions__head p,
.saved-conditions__empty p,
.saved-condition-item span {
  margin: 7px 0 0;
  color: var(--color-text-muted);
  line-height: 1.6;
}

.save-condition-row {
  align-items: end;
}

.save-condition-row .field-label {
  flex: 1;
}

.saved-conditions__empty {
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  background: rgba(17, 75, 95, 0.05);
}

.saved-condition-list {
  display: grid;
  gap: 10px;
}

.saved-condition-item {
  padding: 14px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.7);
}

.saved-condition-item--active {
  border-color: rgba(17, 75, 95, 0.2);
  background: rgba(17, 75, 95, 0.07);
}

.saved-condition-item span {
  display: block;
  font-size: 13px;
}

.saved-condition-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.saved-condition-actions .button {
  min-height: 38px;
  padding: 9px 14px;
}

.milk-tea-toggle {
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
  padding: 16px;
  border-radius: var(--radius-md);
  background: rgba(240, 154, 74, 0.14);
}

.milk-tea-toggle input {
  width: 18px;
  height: 18px;
  margin: 3px 0 0;
}

.milk-tea-toggle strong {
  display: block;
}

.milk-tea-toggle p {
  margin: 6px 0 0;
  color: var(--color-text-muted);
  line-height: 1.6;
}

.form-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.error-text {
  margin: 0;
  color: var(--color-danger);
  font-weight: 700;
}

.result-column {
  display: grid;
  gap: 18px;
}

.result-head {
  align-items: flex-start;
}

.result-metrics {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.result-loading {
  display: grid;
  gap: 10px;
}

.meal-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.meal-item {
  display: grid;
  align-content: start;
  gap: 12px;
  min-height: 190px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.72);
}

.meal-item__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.meal-item__meta span {
  display: inline-flex;
  min-height: 30px;
  padding: 6px 10px;
  border-radius: 999px;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 900;
  background: rgba(17, 75, 95, 0.08);
}

.meal-item__meta strong {
  color: var(--color-text-muted);
  font-size: 12px;
}

.meal-item h3 {
  margin-top: 0;
  font-size: 21px;
  line-height: 1.2;
}

.meal-item p {
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.6;
}

.meal-detail {
  margin-top: 2px;
  padding-top: 10px;
  border-top: 1px solid rgba(17, 75, 95, 0.08);
}

.meal-detail summary {
  width: fit-content;
  cursor: pointer;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 800;
}

.reason-list {
  display: grid;
  gap: 6px;
  margin: 12px 0 0;
  padding: 0;
  list-style: none;
}

.reason-list li {
  position: relative;
  padding-left: 14px;
  color: var(--color-text-muted);
  font-size: 14px;
  line-height: 1.55;
}

.reason-list li::before {
  position: absolute;
  top: 0.72em;
  left: 0;
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: var(--color-primary);
  content: "";
}

.result-summary {
  padding-top: 4px;
  border-top: 1px solid var(--color-border);
}

.tip-list {
  display: grid;
  gap: 12px;
}

.tip-item {
  padding: 14px 16px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.58);
}

.tip-item strong {
  display: block;
}

@media (max-width: 1040px) {
  .recommend-layout,
  .meal-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .section-head,
  .form-footer,
  .saved-conditions__head,
  .save-condition-row,
  .saved-condition-item {
    flex-direction: column;
    align-items: stretch;
  }

  .result-metrics {
    justify-content: flex-start;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .saved-condition-actions {
    justify-content: stretch;
  }

  .saved-condition-actions .button {
    flex: 1;
  }
}
</style>
