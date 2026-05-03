<script setup>
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";

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
      error.message || "生成失败，请确认后端已启动，并且已经导入菜品数据。";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="page recommend-page">
    <section class="panel hero-panel">
      <div>
        <p class="section-kicker">Recommendation Flow</p>
        <h1 class="section-title">根据今天的状态，生成一份更像你的三餐方案。</h1>
        <p class="section-desc">
          预算、口味、忌口、健康目标和奶茶摄入都会参与匹配。生成成功后，结果会自动写入历史记录页，方便后续回顾。
        </p>
      </div>

      <div class="hero-actions">
        <button class="ghost-button" type="button" @click="router.push('/upload')">
          先去导入菜品
        </button>

        <button class="secondary-button" type="button" @click="router.push('/history')">
          查看历史记录
        </button>
      </div>
    </section>

    <section class="recommend-layout">
      <article class="panel form-panel">
        <div class="panel-header">
          <div>
            <h2>填写推荐条件</h2>
            <p>信息越贴近今天的真实状态，结果就越像你会自己选出来的那份菜单。</p>
          </div>

          <button class="ghost-button" type="button" @click="clearForm">清空条件</button>
        </div>

        <div class="form-grid">
          <label class="field-label">
            今日预算 / 元
            <input
              v-model.number="form.budget"
              class="field-input"
              type="number"
              min="0"
              placeholder="例如 60"
            >
          </label>

          <label class="field-label">
            健康目标
            <select v-model="form.goal" class="field-select">
              <option value="">无特殊目标</option>
              <option value="减脂">减脂</option>
              <option value="增肌">增肌</option>
              <option value="均衡饮食">均衡饮食</option>
            </select>
          </label>

          <label class="field-label">
            口味偏好
            <input
              v-model="form.taste"
              class="field-input"
              type="text"
              placeholder="例如 清淡、微辣、咸香"
            >
          </label>

          <label class="field-label">
            忌口关键词
            <input
              v-model="form.dislike"
              class="field-input"
              type="text"
              placeholder="例如 香菜、肥肉、海鲜"
            >
          </label>

          <label class="field-label full-width">
            今天突然很想吃
            <input
              v-model="form.want"
              class="field-input"
              type="text"
              placeholder="例如 牛肉、米饭、面、轻食"
            >
          </label>

          <label class="milk-tea-toggle full-width">
            <input v-model="form.hadMilkTea" type="checkbox">
            <span>今天已经喝过奶茶，希望推荐时尽量避开高糖饮品</span>
          </label>
        </div>

        <div class="form-actions">
          <button
            class="primary-button"
            type="button"
            :disabled="loading"
            @click="generateRecommend"
          >
            {{ loading ? "生成中..." : "生成今日推荐" }}
          </button>

          <span class="status-pill neutral">推荐完成后会自动保存到历史记录</span>
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      </article>

      <aside class="panel tips-panel">
        <h2>输入建议</h2>

        <div class="tip-list">
          <article class="tip-item">
            <strong>预算不是越精确越好</strong>
            <p>给一个今天能接受的范围即可，规则会优先找更贴近预算的菜品。</p>
          </article>

          <article class="tip-item">
            <strong>口味和“突然想吃”可以分开填</strong>
            <p>前者适合填长期偏好，后者更适合当天情绪化的小冲动。</p>
          </article>

          <article class="tip-item">
            <strong>忌口关键词支持多个</strong>
            <p>可以用逗号、空格或顿号分隔，系统会自动拆分处理。</p>
          </article>
        </div>
      </aside>
    </section>

    <section v-if="result" class="panel result-panel">
      <div class="result-header">
        <div>
          <p class="section-kicker">Generated Result</p>
          <h2>今日推荐已经生成</h2>
        </div>

        <div class="result-metrics">
          <span class="status-pill success">预计总价 {{ result.totalPrice ?? 0 }} 元</span>
          <span class="status-pill neutral">预算结余 {{ result.remainingBudget ?? 0 }} 元</span>
        </div>
      </div>

      <div class="meal-grid">
        <article v-for="meal in mealCards" :key="meal.type" class="meal-card">
          <span>{{ meal.type }}</span>
          <h3>{{ meal.name }}</h3>
          <p>{{ meal.reason }}</p>
        </article>
      </div>

      <div class="summary-card">
        <h3>推荐总结</h3>
        <p>{{ result.summary }}</p>

        <div class="summary-actions">
          <button class="secondary-button" type="button" @click="router.push('/history')">
            去历史页查看
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero-panel,
.form-panel,
.tips-panel,
.result-panel {
  padding: 30px;
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 12px;
}

.recommend-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.62fr);
  gap: 20px;
}

.panel-header,
.result-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
}

.panel-header h2,
.tips-panel h2,
.result-header h2,
.summary-card h3,
.meal-card h3 {
  margin: 0;
}

.panel-header p,
.tip-item p,
.meal-card p,
.summary-card p {
  margin: 10px 0 0;
  color: var(--text-secondary);
  line-height: 1.78;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-top: 24px;
}

.full-width {
  grid-column: 1 / -1;
}

.milk-tea-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px;
  border-radius: 20px;
  font-weight: 700;
  color: var(--accent-primary);
  background: rgba(255, 140, 66, 0.14);
}

.milk-tea-toggle input {
  width: 18px;
  height: 18px;
}

.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-top: 24px;
}

.error-text {
  margin: 18px 0 0;
  color: var(--danger);
  font-weight: 800;
}

.tips-panel {
  display: grid;
  align-content: start;
  gap: 18px;
}

.tip-list {
  display: grid;
  gap: 14px;
}

.tip-item {
  padding: 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.68);
}

.tip-item strong {
  display: block;
}

.result-metrics {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.meal-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 22px;
}

.meal-card {
  padding: 22px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.76);
}

.meal-card span {
  display: inline-flex;
  padding: 8px 12px;
  border-radius: 999px;
  color: var(--accent-primary);
  font-size: 13px;
  font-weight: 900;
  background: rgba(17, 75, 95, 0.08);
}

.meal-card h3 {
  margin-top: 14px;
  font-size: 24px;
}

.summary-card {
  margin-top: 18px;
  padding: 22px;
  border-radius: 24px;
  background:
    radial-gradient(circle at right top, rgba(255, 140, 66, 0.12), transparent 40%),
    rgba(255, 255, 255, 0.74);
}

.summary-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

@media (max-width: 980px) {
  .hero-panel,
  .recommend-layout,
  .meal-grid {
    grid-template-columns: 1fr;
  }

  .hero-panel,
  .panel-header,
  .result-header {
    flex-direction: column;
  }

  .hero-actions,
  .result-metrics {
    justify-content: flex-start;
  }
}

@media (max-width: 680px) {
  .hero-panel,
  .form-panel,
  .tips-panel,
  .result-panel {
    padding: 22px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-actions,
  .summary-actions {
    display: grid;
  }

  .form-actions button,
  .summary-actions button {
    width: 100%;
  }
}
</style>
