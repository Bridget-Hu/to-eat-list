<script setup>
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import AppCard from "@/components/AppCard.vue";
import EmptyState from "@/components/EmptyState.vue";
import PageHeader from "@/components/PageHeader.vue";
import { requestJson } from "@/utils/api";

defineOptions({
  name: "RecommendPage"
});

const router = useRouter();

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

const mealCards = computed(() => {
  if (!result.value) {
    return [];
  }

  return [
    {
      type: "早餐",
      name: result.value.breakfast,
      reason: result.value.breakfastReason
    },
    {
      type: "午餐",
      name: result.value.lunch,
      reason: result.value.lunchReason
    },
    {
      type: "晚餐",
      name: result.value.dinner,
      reason: result.value.dinnerReason
    }
  ];
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
    errorMessage.value =
      error.message || "生成失败，请先确认后端已启动并且已经导入菜品数据。";
  } finally {
    loading.value = false;
  }
}
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
              <option value="">无特殊目标</option>
              <option value="减脂">减脂</option>
              <option value="增肌">增肌</option>
              <option value="均衡饮食">均衡饮食</option>
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

        <div class="form-footer">
          <div class="button-row">
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
                :key="meal.type"
                class="meal-item"
              >
                <span>{{ meal.type }}</span>
                <h3>{{ meal.name }}</h3>
                <p>{{ meal.reason }}</p>
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
.meal-item p,
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

.meal-item h3 {
  margin-top: 12px;
  font-size: 21px;
  line-height: 1.2;
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
  .form-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .result-metrics {
    justify-content: flex-start;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
