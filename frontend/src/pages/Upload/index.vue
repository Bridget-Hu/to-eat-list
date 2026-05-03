<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

import { API_BASE } from "@/utils/api";

defineOptions({
  name: "UploadPage"
});

const router = useRouter();

const fileInput = ref(null);
const selectedFile = ref(null);
const statusText = ref("请选择 txt / csv / doc / docx 文件");
const statusType = ref("neutral");
const loading = ref(false);
const imported = ref(false);
const importedCount = ref(0);

function openFilePicker() {
  fileInput.value?.click();
}

async function handleFileChange(event) {
  const file = event.target.files?.[0];

  if (!file) {
    selectedFile.value = null;
    imported.value = false;
    importedCount.value = 0;
    statusText.value = "暂未选择文件";
    statusType.value = "neutral";
    return;
  }

  selectedFile.value = file;
  imported.value = false;
  importedCount.value = 0;
  loading.value = true;
  statusText.value = "正在解析并导入菜品数据...";
  statusType.value = "warning";

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE}/foods/upload`, {
      method: "POST",
      body: formData
    });

    let data = null;

    try {
      data = await response.json();
    } catch {
      data = null;
    }

    if (!response.ok) {
      throw new Error(data?.detail || data?.message || "导入失败，请检查文件格式。");
    }

    imported.value = true;
    importedCount.value = data?.count ?? 0;
    statusText.value = `导入成功，已写入 ${importedCount.value} 个菜品。`;
    statusType.value = "success";
  } catch (error) {
    imported.value = false;
    importedCount.value = 0;
    statusText.value = error.message || "导入失败，请确认后端服务已启动。";
    statusType.value = "danger";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="page upload-page">
    <section class="panel intro-panel">
      <div>
        <p class="section-kicker">Food Source</p>
        <h1 class="section-title">先把菜品池整理好，推荐才会更靠谱。</h1>
        <p class="section-desc">
          上传文件后，系统会把菜品名称、分类、价格、口味和备注写入后端数据源，后续推荐和历史记录都会基于这一批数据工作。
        </p>
      </div>

      <div class="intro-badges">
        <span class="status-pill neutral">支持 txt / csv / doc / docx</span>
        <span class="status-pill warning">建议先整理好列名与价格</span>
      </div>
    </section>

    <section class="upload-layout">
      <article class="panel upload-panel">
        <input
          ref="fileInput"
          type="file"
          accept=".txt,.csv,.doc,.docx"
          hidden
          @change="handleFileChange"
        />

        <div class="upload-core">
          <div class="upload-icon">食</div>

          <h2>导入外卖与食堂菜品</h2>
          <p>
            支持一次性把你常吃的早餐、午餐、晚餐、饮品和加餐整理进来，减少每天重复录入。
          </p>

          <button
            class="primary-button"
            type="button"
            :disabled="loading"
            @click="openFilePicker"
          >
            {{ loading ? "导入中..." : selectedFile ? "重新选择文件" : "选择文件并导入" }}
          </button>
        </div>

        <div class="upload-status">
          <div>
            <span class="status-label">当前文件</span>
            <strong>{{ selectedFile ? selectedFile.name : "尚未选择文件" }}</strong>
          </div>

          <span class="status-pill" :class="statusType">
            {{ statusText }}
          </span>
        </div>

        <div class="panel success-panel" :class="{ visible: imported }">
          <strong>导入完成</strong>
          <p>
            现在可以直接去生成推荐，或者稍后在历史记录页回看系统为你生成过的菜单。
          </p>

          <div class="success-actions">
            <button class="secondary-button" type="button" @click="router.push('/')">
              返回首页
            </button>

            <button
              class="primary-button"
              type="button"
              :disabled="!imported"
              @click="router.push('/recommend')"
            >
              开始生成推荐
            </button>
          </div>
        </div>
      </article>

      <aside class="panel tips-panel">
        <h2>整理建议</h2>

        <div class="tip-list">
          <article class="tip-item">
            <span>01</span>
            <div>
              <strong>补齐价格和分类</strong>
              <p>这样推荐阶段才能更好地控制预算，并区分早午晚餐。</p>
            </div>
          </article>

          <article class="tip-item">
            <span>02</span>
            <div>
              <strong>口味标签尽量具体</strong>
              <p>比如“清淡”“微辣”“高蛋白”，后端规则会直接参考这些关键词。</p>
            </div>
          </article>

          <article class="tip-item">
            <span>03</span>
            <div>
              <strong>备注写真实体验</strong>
              <p>像“适合赶时间”“容易腻”“减脂友好”这类备注，会让推荐更像你自己的选择。</p>
            </div>
          </article>
        </div>
      </aside>
    </section>
  </div>
</template>

<style scoped>
.intro-panel {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
  padding: 30px;
}

.intro-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 12px;
}

.upload-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.62fr);
  gap: 20px;
}

.upload-panel,
.tips-panel {
  padding: 28px;
}

.upload-core {
  display: grid;
  justify-items: center;
  gap: 16px;
  padding: 32px;
  border: 2px dashed rgba(17, 75, 95, 0.18);
  border-radius: 28px;
  background:
    radial-gradient(circle at top, rgba(255, 140, 66, 0.12), transparent 54%),
    rgba(255, 255, 255, 0.7);
  text-align: center;
}

.upload-icon {
  display: grid;
  place-items: center;
  width: 72px;
  height: 72px;
  border-radius: 24px;
  color: white;
  font-size: 28px;
  font-weight: 900;
  background: linear-gradient(135deg, var(--accent-secondary), #ffb36d);
  box-shadow: 0 18px 34px rgba(255, 140, 66, 0.22);
}

.upload-core h2,
.tips-panel h2,
.success-panel strong,
.tip-item strong {
  margin: 0;
}

.upload-core p,
.success-panel p,
.tip-item p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.75;
}

.upload-status {
  display: grid;
  gap: 14px;
  margin-top: 18px;
  padding: 18px 20px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.68);
}

.status-label {
  display: block;
  margin-bottom: 6px;
  color: var(--text-secondary);
  font-size: 13px;
}

.success-panel {
  display: none;
  gap: 14px;
  margin-top: 18px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.72);
}

.success-panel.visible {
  display: grid;
}

.success-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tips-panel {
  display: grid;
  align-content: start;
  gap: 20px;
}

.tip-list {
  display: grid;
  gap: 14px;
}

.tip-item {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
  padding: 16px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.72);
}

.tip-item span {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 14px;
  color: var(--accent-primary);
  font-size: 13px;
  font-weight: 900;
  background: rgba(17, 75, 95, 0.1);
}

@media (max-width: 980px) {
  .intro-panel,
  .upload-layout {
    grid-template-columns: 1fr;
  }

  .intro-panel {
    flex-direction: column;
  }

  .intro-badges {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .intro-panel,
  .upload-panel,
  .tips-panel {
    padding: 22px;
  }

  .upload-core {
    padding: 24px 18px;
  }

  .success-actions {
    display: grid;
  }

  .success-actions button {
    width: 100%;
  }
}
</style>
