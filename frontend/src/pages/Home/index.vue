<template>
  <main class="home-page">
    <section class="hero">
      <p class="tag">Campus Meal Decision Assistant</p>

      <h1>校园吃饭决策助手</h1>

      <p class="intro">
        帮你把校园外卖、食堂菜品、预算、口味偏好、忌口和搭配数据统一导入，
        后续可交给 AI 后端进行饮食推荐和一日三餐规划。
      </p>

      <div class="hero-actions">
        <button class="primary-btn" @click="$emit('go-upload')">开始上传</button>
        <button class="secondary-btn" @click="$emit('go-upload')">批量导入菜品数据</button>
      </div>
    </section>

    <section class="feature-grid">
      <div class="feature-card">
        <h3>批量导入</h3>
        <p>不再一个个手动输入菜品，直接上传整理好的本地文档。</p>
      </div>

      <div class="feature-card">
        <h3>支持 txt / Word</h3>
        <p>支持 txt、doc、docx 文件，方便一次性录入菜品数据。</p>
      </div>

      <div class="feature-card">
        <h3>预留后端接口</h3>
        <p>前端负责上传文件，后续存储、解析、AI 推荐交给后端。</p>
      </div>
    </section>
  </main>
</template>

<style scoped>
.home-page {
  padding: 72px 8% 80px;
}

.hero {
  max-width: 820px;
  margin: 0 auto;
  text-align: center;
}

.tag {
  display: inline-block;
  margin-bottom: 18px;
  padding: 8px 16px;
  border-radius: 999px;
  background: #e0edff;
  color: #2563eb;
  font-weight: 700;
}

.hero h1 {
  margin: 0;
  font-size: 56px;
}

.intro {
  margin: 24px auto 0;
  max-width: 680px;
  color: #64748b;
  font-size: 18px;
  line-height: 1.8;
}

.hero-actions {
  margin-top: 36px;
  display: flex;
  justify-content: center;
  gap: 16px;
}

.primary-btn,
.secondary-btn {
  border: none;
  cursor: pointer;
  border-radius: 999px;
  font-size: 15px;
}

.primary-btn {
  padding: 14px 28px;
  background: #2563eb;
  color: white;
  font-weight: 700;
}

.secondary-btn {
  padding: 14px 28px;
  background: white;
  color: #2563eb;
  font-weight: 700;
  border: 1px solid #dbeafe;
}

.feature-grid {
  max-width: 1040px;
  margin: 72px auto 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
}

.feature-card {
  padding: 28px;
  border-radius: 24px;
  background: white;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
}

.feature-card h3 {
  margin: 0 0 12px;
  font-size: 22px;
}

.feature-card p {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}
</style>