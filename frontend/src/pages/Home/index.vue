<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { getOverviewStats } from "@/api/stats";
import AppCard from "@/components/AppCard.vue";
import PageHeader from "@/components/PageHeader.vue";
import StatCard from "@/components/StatCard.vue";
import { errorCopy } from "@/utils/copy";

defineOptions({
  name: "HomePage"
});

const router = useRouter();
const overviewLoading = ref(false);
const overviewError = ref("");
const overviewStats = ref({
  foodCount: 0,
  historyCount: 0
});

const quickActions = [
  {
    title: "开始推荐",
    desc: "填写今天的预算、口味、忌口和健康目标，直接生成一日三餐建议。",
    path: "/recommend",
    eyebrow: "核心入口"
  },
  {
    title: "导入菜品",
    desc: "先把食堂、外卖和常吃店铺整理进来，推荐结果会更贴近真实选择。",
    path: "/upload",
    eyebrow: "数据准备"
  },
  {
    title: "查看历史记录",
    desc: "回看最近吃了什么、预算控制得如何，以及哪些偏好最常出现。",
    path: "/history",
    eyebrow: "自动存档"
  }
];

const steps = [
  {
    step: "01",
    title: "导入菜品",
    desc: "整理店名、价格、分类、标签和备注。"
  },
  {
    step: "02",
    title: "填写今天的状态",
    desc: "预算、口味、忌口、目标一次填完。"
  },
  {
    step: "03",
    title: "生成并自动保存",
    desc: "推荐结果会直接写入历史记录，方便回看。"
  }
];

const highlights = [
  "首页压缩为更短的决策入口，不再堆叠大段展示型内容。",
  "推荐页改成左右工具布局，表单和结果可以尽量同屏查看。",
  "历史页优先展示列表，减少无关装饰，先看到你真正要找的记录。"
];

function goTo(path) {
  router.push(path);
}

function formatOverviewValue(value) {
  if (overviewLoading.value) {
    return "...";
  }

  if (overviewError.value) {
    return "--";
  }

  return Number(value || 0);
}

async function loadOverviewStats() {
  overviewLoading.value = true;
  overviewError.value = "";

  try {
    const data = await getOverviewStats();
    overviewStats.value = {
      foodCount: Number(data?.food_count || 0),
      historyCount: Number(data?.history_count || 0)
    };
  } catch (error) {
    overviewError.value = error.message || errorCopy.overviewLoad;
  } finally {
    overviewLoading.value = false;
  }
}

onMounted(() => {
  loadOverviewStats();
});
</script>

<template>
  <div class="page home-page">
    <AppCard class="home-hero" tone="accent" padding="lg">
      <PageHeader
        eyebrow="Campus Meal Planner"
        title="把“今天吃什么”变成一个更快、更轻松的决定"
        description="To-Eat-List 把导入菜品、填写条件、生成推荐和历史回看放进同一条短流程里。首页只保留真正高频的入口，让你少跳一步、少想一层。"
      >
        <template #meta>
          <span class="status-pill status-pill--primary">3 步完成一次推荐</span>
          <span class="status-pill status-pill--neutral">生成后自动保存历史</span>
          <span v-if="overviewError" class="status-pill status-pill--danger">
            概览暂不可用
          </span>
        </template>

        <template #actions>
          <button
            class="button button--primary"
            type="button"
            @click="goTo('/recommend')"
          >
            开始推荐
          </button>
          <button
            class="button button--ghost"
            type="button"
            @click="goTo('/upload')"
          >
            导入菜品
          </button>
        </template>
      </PageHeader>

      <div class="home-hero__grid">
        <div class="home-actions">
          <AppCard
            v-for="item in quickActions"
            :key="item.path"
            as="button"
            type="button"
            padding="md"
            interactive
            class="home-action"
            :class="{ 'home-action--wide': item.path === '/history' }"
            @click="goTo(item.path)"
          >
            <span class="home-action__eyebrow">{{ item.eyebrow }}</span>
            <strong>{{ item.title }}</strong>
            <p>{{ item.desc }}</p>
          </AppCard>
        </div>

        <div class="workflow-panel">
          <div class="workflow-panel__head">
            <span class="status-pill status-pill--warning">今日流程</span>
            <p>先准备数据，再根据当天状态做选择，最后把推荐留在历史里。</p>
          </div>

          <div class="workflow-list">
            <article
              v-for="item in steps"
              :key="item.step"
              class="workflow-item"
            >
              <span>{{ item.step }}</span>
              <div>
                <strong>{{ item.title }}</strong>
                <p>{{ item.desc }}</p>
              </div>
            </article>
          </div>
        </div>
      </div>
    </AppCard>

    <section class="home-stats">
      <StatCard
        label="正式菜品数量"
        :value="formatOverviewValue(overviewStats.foodCount)"
        hint="当前 SQLite 菜品库中的可推荐菜品数。"
      />
      <StatCard
        label="历史记录数量"
        :value="formatOverviewValue(overviewStats.historyCount)"
        hint="已经沉淀下来的推荐历史总数。"
      />
      <StatCard label="核心流程" value="导入 > 推荐 > 回看" hint="从数据准备到记录沉淀连成一条线。" />
      <StatCard label="推荐视角" value="预算 + 偏好" hint="既考虑今天想吃什么，也照顾健康目标。" />
      <StatCard label="使用方式" value="工具化首屏" hint="先看到高频动作，而不是一整页宣传内容。" />
    </section>

    <section class="highlight-grid">
      <AppCard
        v-for="item in highlights"
        :key="item"
        padding="md"
        tone="muted"
        class="highlight-card"
      >
        <span></span>
        <p>{{ item }}</p>
      </AppCard>
    </section>
  </div>
</template>

<style scoped>
.home-hero {
  display: grid;
  gap: 24px;
}

.home-hero__grid {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(300px, 0.95fr);
  gap: 18px;
}

.home-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.home-action {
  width: 100%;
  text-align: left;
  appearance: none;
  cursor: pointer;
}

.home-action--wide {
  grid-column: 1 / -1;
}

.home-action__eyebrow {
  color: var(--color-accent);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.home-action strong,
.workflow-item strong {
  display: block;
  margin-top: 10px;
  font-size: 21px;
  line-height: 1.2;
}

.home-action p,
.workflow-panel__head p,
.workflow-item p,
.highlight-card p {
  margin: 10px 0 0;
  color: var(--color-text-muted);
  line-height: 1.7;
}

.workflow-panel {
  display: grid;
  gap: 16px;
  padding: 20px;
  border-radius: var(--radius-lg);
  color: #fff;
  background:
    linear-gradient(155deg, rgba(17, 75, 95, 0.96), rgba(27, 114, 133, 0.92)),
    linear-gradient(135deg, rgba(240, 154, 74, 0.24), transparent);
  box-shadow: var(--shadow-glow);
}

.workflow-panel__head {
  display: grid;
  gap: 10px;
}

.workflow-panel__head p {
  color: rgba(255, 255, 255, 0.82);
}

.workflow-list {
  display: grid;
  gap: 12px;
}

.workflow-item {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
  padding: 14px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.1);
}

.workflow-item span {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 900;
  background: #fff2e3;
}

.workflow-item strong {
  margin-top: 0;
  font-size: 16px;
}

.workflow-item p {
  color: rgba(255, 255, 255, 0.76);
}

.home-stats,
.highlight-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.highlight-card {
  display: grid;
  grid-template-columns: 12px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.highlight-card span {
  width: 12px;
  height: 12px;
  margin-top: 6px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--color-accent), #ffbc82);
}

@media (max-width: 980px) {
  .home-hero__grid,
  .home-stats,
  .highlight-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .home-actions {
    grid-template-columns: 1fr;
  }

  .home-action--wide {
    grid-column: auto;
  }
}
</style>
