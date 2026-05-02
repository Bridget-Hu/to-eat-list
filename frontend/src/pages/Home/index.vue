<template>
  <main class="home-page">
    <section class="hero">
      <p class="tag">Campus Meal Decision Assistant</p>

      <h1>校园吃饭决策助手</h1>

      <p class="intro">
        帮你把校园外卖、食堂菜品、预算、口味偏好、忌口和搭配数据统一管理，
        先导入菜品数据，再根据你的需求生成一日三餐推荐。
      </p>

      <div class="hero-actions">
        <button class="primary-btn" @click="$router.push('/upload')">
          导入菜品数据
        </button>

        <button class="recommend-btn" @click="$router.push('/recommend')">
          生成今日推荐
        </button>
      </div>
    </section>

    <section class="feature-grid">
      <div class="feature-card">
        <h3>批量导入</h3>
        <p>支持一次性上传整理好的菜品文档，减少手动录入的麻烦。</p>
      </div>

      <div class="feature-card">
        <h3>个性化条件</h3>
        <p>可以填写预算、口味偏好、忌口、健康目标和今天想吃什么。</p>
      </div>

      <div class="feature-card">
        <h3>规则推荐</h3>
        <p>先使用规则推荐生成一日三餐，后续可以继续接入 AI 后端。</p>
      </div>
    </section>
  </main>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  padding: 64px 8%;
  background: linear-gradient(135deg, #eef6ff 0%, #f8fbff 100%);
  color: #0f172a;
}

.hero {
  max-width: 1080px;
  margin: 0 auto;
  padding: 56px 48px;
  border-radius: 32px;
  background: white;
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.1);
}

.tag {
  margin: 0 0 14px;
  color: #2563eb;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: clamp(38px, 6vw, 64px);
  line-height: 1.05;
  color: #0f172a;
}

.intro {
  max-width: 760px;
  margin: 22px 0 0;
  color: #64748b;
  font-size: 17px;
  line-height: 1.9;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 34px;
}

button {
  border: none;
  border-radius: 999px;
  padding: 14px 26px;
  font-weight: 900;
  cursor: pointer;
  transition: 0.2s ease;
}

button:hover {
  transform: translateY(-2px);
}

.primary-btn {
  color: white;
  background: linear-gradient(135deg, #2563eb, #0ea5e9);
  box-shadow: 0 14px 34px rgba(37, 99, 235, 0.28);
}

.recommend-btn {
  color: white;
  background: linear-gradient(135deg, #f97316, #fb923c);
  box-shadow: 0 14px 30px rgba(249, 115, 22, 0.24);
}

.feature-grid {
  max-width: 1080px;
  margin: 28px auto 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.feature-card {
  padding: 28px;
  border-radius: 24px;
  background: white;
  border: 1px solid #dbeafe;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.06);
}

.feature-card h3 {
  margin: 0 0 10px;
  color: #0f172a;
  font-size: 20px;
}

.feature-card p {
  margin: 0;
  color: #64748b;
  line-height: 1.8;
}

@media (max-width: 820px) {
  .home-page {
    padding: 36px 5%;
  }

  .hero {
    padding: 36px 26px;
  }

  .hero-actions {
    flex-direction: column;
  }

  button {
    width: 100%;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }
}
</style>