<template>
  <main class="recommend-page">
    <section class="hero-card">
      <div>
        <p class="tag">Campus Meal Assistant</p>
        <h1>生成今日一日三餐</h1>
        <p>
          根据预算、口味偏好、忌口和今天想吃的内容，由后端根据已上传菜品生成推荐。
        </p>
      </div>

      <button type="button" @click="goUpload">先去导入菜品</button>
    </section>

    <section class="main-card">
      <h2>填写推荐条件</h2>

      <div class="form-grid">
        <label>
          今日预算 / 元
          <input
            v-model.number="form.budget"
            type="number"
            placeholder="例如 60"
          />
        </label>

        <label>
          健康目标
          <select v-model="form.goal">
            <option value="">无特殊目标</option>
            <option value="减脂">减脂</option>
            <option value="增肌">增肌</option>
            <option value="均衡饮食">均衡饮食</option>
          </select>
        </label>

        <label>
          口味偏好
          <input
            v-model="form.taste"
            placeholder="例如 清淡、微辣、咸香"
          />
        </label>

        <label>
          忌口
          <input
            v-model="form.dislike"
            placeholder="例如 肥肉、香菜、海鲜"
          />
        </label>

        <label class="full">
          今天突然想吃
          <input
            v-model="form.want"
            placeholder="例如 牛肉、米饭、面条、轻食"
          />
        </label>

        <label class="checkbox-card full">
          <input v-model="form.hadMilkTea" type="checkbox" />
          <span>今天已经喝过奶茶</span>
        </label>
      </div>

      <div class="actions">
        <button
          class="primary"
          type="button"
          :disabled="loading"
          @click="generateRecommend"
        >
          {{ loading ? "生成中..." : "生成推荐" }}
        </button>

        <button class="secondary" type="button" @click="clearForm">
          清空条件
        </button>
      </div>

      <p v-if="errorMessage" class="error-text">
        {{ errorMessage }}
      </p>
    </section>

    <section v-if="result" class="result-card">
      <h2>今日推荐</h2>

      <div class="meal-grid">
        <article>
          <span>早餐</span>
          <h3>{{ result.breakfast }}</h3>
          <p>{{ result.breakfastReason }}</p>
        </article>

        <article>
          <span>午餐</span>
          <h3>{{ result.lunch }}</h3>
          <p>{{ result.lunchReason }}</p>
        </article>

        <article>
          <span>晚餐</span>
          <h3>{{ result.dinner }}</h3>
          <p>{{ result.dinnerReason }}</p>
        </article>
      </div>

      <div class="summary">
        <h3>推荐总结</h3>
        <p>{{ result.summary }}</p>
      </div>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const API_BASE = "http://127.0.0.1:8001";

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
    const response = await fetch(`${API_BASE}/recommend/daily`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(form)
    });

    let data = null;

    try {
      data = await response.json();
    } catch {
      data = null;
    }

    if (!response.ok) {
      throw new Error(
        data?.detail ||
          data?.message ||
          "生成失败，请确认已在上传页成功导入菜品数据。"
      );
    }

    result.value = data;
  } catch (error) {
    console.error(error);
    errorMessage.value =
      error.message || "生成失败，请确认后端已启动，并且端口是 8001。";
  } finally {
    loading.value = false;
  }
}

function goUpload() {
  router.push("/upload");
}
</script>

<style scoped>
.recommend-page {
  min-height: 100vh;
  padding: 42px 8% 72px;
  background: linear-gradient(135deg, #eef6ff, #f8fbff);
  color: #0f172a;
}

.hero-card,
.main-card,
.result-card {
  max-width: 1080px;
  margin: 0 auto 24px;
  padding: 32px;
  border-radius: 28px;
  background: white;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
}

.hero-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  color: white;
  background: linear-gradient(135deg, #2563eb, #0ea5e9);
}

.tag {
  margin: 0 0 8px;
  font-size: 13px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  opacity: 0.85;
  font-weight: 800;
}

h1 {
  margin: 0;
  font-size: 42px;
}

h2 {
  margin: 0 0 22px;
  font-size: 26px;
}

.hero-card p {
  margin: 12px 0 0;
  line-height: 1.8;
  opacity: 0.9;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

label {
  display: grid;
  gap: 8px;
  color: #334155;
  font-weight: 800;
}

.full {
  grid-column: 1 / -1;
}

input,
select {
  height: 46px;
  padding: 0 14px;
  border: 1px solid #dbe3ef;
  border-radius: 14px;
  font-size: 15px;
  outline: none;
}

input:focus,
select:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
}

.checkbox-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px;
  border-radius: 16px;
  background: #fff7ed;
  color: #9a3412;
}

.checkbox-card input {
  width: 18px;
  height: 18px;
}

.actions {
  display: flex;
  gap: 14px;
  margin-top: 26px;
}

button {
  border: none;
  border-radius: 999px;
  padding: 13px 22px;
  font-weight: 900;
  cursor: pointer;
  transition: 0.2s ease;
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.primary {
  color: white;
  background: #2563eb;
}

.secondary {
  color: #2563eb;
  background: #eef4ff;
}

.hero-card button {
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.55);
  background: rgba(255, 255, 255, 0.16);
}

.error-text {
  margin-top: 16px;
  color: #dc2626;
  font-weight: 800;
}

.meal-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.meal-grid article {
  padding: 22px;
  border-radius: 22px;
  background: #f8fbff;
  border: 1px solid #dbeafe;
}

.meal-grid span {
  color: #2563eb;
  font-weight: 900;
}

.meal-grid h3 {
  margin: 12px 0 8px;
}

.meal-grid p,
.summary p {
  margin: 0;
  color: #64748b;
  line-height: 1.8;
}

.summary {
  margin-top: 20px;
  padding: 18px;
  border-radius: 20px;
  background: #f8fafc;
}

.summary h3 {
  margin: 0 0 8px;
}

@media (max-width: 820px) {
  .hero-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-grid,
  .meal-grid {
    grid-template-columns: 1fr;
  }

  h1 {
    font-size: 34px;
  }
}
</style>