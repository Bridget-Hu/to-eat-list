<script setup>
import { useRouter } from "vue-router";

defineOptions({
  name: "HomePage"
});

const router = useRouter();

const quickLinks = [
  {
    title: "导入菜品",
    desc: "先把学校周边外卖、食堂和常吃店铺整理进系统。",
    path: "/upload"
  },
  {
    title: "生成推荐",
    desc: "根据预算、口味、目标和今天状态快速出一日三餐。",
    path: "/recommend"
  },
  {
    title: "查看历史",
    desc: "回顾最近吃了什么、预算花了多少、哪些偏好最常出现。",
    path: "/history"
  }
];

const highlights = [
  "把上传、推荐、回顾放进同一条流程，少跳转、少记忆负担。",
  "针对预算、口味、忌口和奶茶摄入做快速筛选。",
  "历史页保留真实推荐结果，方便观察最近饮食节奏。"
];

const steps = [
  {
    step: "01",
    title: "整理可选菜品",
    desc: "把店名、价格、口味标签和备注导入进来。"
  },
  {
    step: "02",
    title: "填写今天状态",
    desc: "预算、口味目标、突然想吃什么，一次填完。"
  },
  {
    step: "03",
    title: "查看推荐与回顾",
    desc: "系统给出一日三餐，并自动沉淀进历史记录。"
  }
];

function goTo(path) {
  router.push(path);
}
</script>

<template>
  <div class="page home-page">
    <section class="panel hero-panel">
      <div class="hero-copy">
        <p class="section-kicker">Campus Meal Planner</p>
        <h1 class="section-title">把“今天吃什么”变成一个轻松决定。</h1>
        <p class="section-desc">
          To-Eat-List
          现在不只是一个推荐入口，也是一条完整饮食流程。先整理菜品，再生成推荐，最后用历史记录回看最近的选择、预算和口味变化。
        </p>

        <div class="hero-actions">
          <button class="primary-button" type="button" @click="goTo('/recommend')">
            开始今日推荐
          </button>

          <button class="ghost-button" type="button" @click="goTo('/history')">
            打开历史记录
          </button>
        </div>
      </div>

      <div class="hero-board">
        <div class="board-top">
          <span class="board-chip">推荐流程</span>
          <strong>从犹豫到决定，用一屏走完</strong>
        </div>

        <div class="board-list">
          <article v-for="item in steps" :key="item.step" class="board-item">
            <span>{{ item.step }}</span>
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="quick-grid">
      <button
        v-for="item in quickLinks"
        :key="item.path"
        type="button"
        class="panel quick-card"
        @click="goTo(item.path)"
      >
        <span>快速入口</span>
        <h2>{{ item.title }}</h2>
        <p>{{ item.desc }}</p>
      </button>
    </section>

    <section class="panel insight-panel">
      <div>
        <p class="section-kicker">Why It Feels Better</p>
        <h2 class="insight-title">这次首页顺手把项目主线也理顺了。</h2>
      </div>

      <div class="insight-list">
        <article v-for="item in highlights" :key="item" class="insight-item">
          <span></span>
          <p>{{ item }}</p>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-page {
  padding-bottom: 28px;
}

.hero-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  gap: 24px;
  padding: 36px;
}

.hero-copy {
  display: grid;
  align-content: center;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 28px;
}

.hero-board {
  display: grid;
  gap: 18px;
  padding: 24px;
  border-radius: 26px;
  color: white;
  background:
    linear-gradient(155deg, rgba(17, 75, 95, 0.96), rgba(11, 118, 141, 0.88)),
    linear-gradient(135deg, rgba(255, 140, 66, 0.26), transparent);
  box-shadow: 0 20px 44px rgba(17, 75, 95, 0.24);
}

.board-top {
  display: grid;
  gap: 10px;
}

.board-top strong {
  font-size: 26px;
  line-height: 1.2;
}

.board-chip {
  justify-self: start;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  color: #ffe9d5;
  background: rgba(255, 255, 255, 0.14);
}

.board-list {
  display: grid;
  gap: 14px;
}

.board-item {
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
  padding: 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
}

.board-item span {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 16px;
  font-weight: 900;
  color: var(--accent-primary);
  background: #fff2e6;
}

.board-item h3,
.quick-card h2,
.insight-title {
  margin: 0;
}

.board-item p,
.quick-card p,
.insight-item p {
  margin: 8px 0 0;
  line-height: 1.7;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.quick-card {
  text-align: left;
  padding: 24px;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.quick-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 26px 40px rgba(69, 50, 36, 0.16);
}

.quick-card span {
  color: var(--accent-secondary);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.quick-card h2 {
  margin-top: 14px;
  font-size: 28px;
}

.quick-card p {
  color: var(--text-secondary);
}

.insight-panel {
  display: grid;
  grid-template-columns: minmax(260px, 0.78fr) minmax(0, 1fr);
  gap: 24px;
  padding: 30px;
}

.insight-title {
  font-size: 32px;
  line-height: 1.2;
}

.insight-list {
  display: grid;
  gap: 14px;
}

.insight-item {
  display: grid;
  grid-template-columns: 14px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
  padding: 18px 20px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.7);
}

.insight-item span {
  width: 14px;
  height: 14px;
  margin-top: 6px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent-secondary), #ffb36d);
}

@media (max-width: 980px) {
  .hero-panel,
  .insight-panel,
  .quick-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hero-panel,
  .insight-panel {
    padding: 24px;
  }

  .hero-actions {
    display: grid;
  }

  .hero-actions button {
    width: 100%;
  }

  .quick-card h2 {
    font-size: 24px;
  }
}
</style>
