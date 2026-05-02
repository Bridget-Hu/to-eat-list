<template>
  <main class="upload-page">
    <section class="upload-card">
      <p class="tag">Data Upload</p>

      <h1>导入菜品数据</h1>

      <p class="desc">
        选择整理好的 txt / csv 文件，系统会把菜品发送给后端保存，后续推荐会基于这些菜品生成。
      </p>

      <div class="upload-box">
        <input
          ref="fileInput"
          type="file"
          accept=".txt,.csv,.doc,.docx"
          hidden
          @change="handleFileChange"
        />

        <button
          class="choose-btn"
          type="button"
          :disabled="loading"
          @click="openFilePicker"
        >
          {{ loading ? "导入中..." : selectedFile ? "重新选择文件" : "选择文件并导入" }}
        </button>

        <p class="file-name">
          {{ selectedFile ? selectedFile.name : "暂未选择文件" }}
        </p>

        <p class="status" :class="statusType">
          {{ statusText }}
        </p>
      </div>

      <div class="actions">
        <button class="secondary-btn" type="button" @click="goHome">
          返回首页
        </button>

        <button
          class="recommend-btn"
          type="button"
          :disabled="!imported"
          @click="goRecommend"
        >
          开始推荐
        </button>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const API_BASE = "http://127.0.0.1:8001";

const fileInput = ref(null);
const selectedFile = ref(null);
const statusText = ref("请选择 txt / csv / doc / docx 文件");
const statusType = ref("");
const loading = ref(false);
const imported = ref(false);

function openFilePicker() {
  fileInput.value?.click();
}

async function handleFileChange(event) {
  const file = event.target.files[0];

  if (!file) {
    selectedFile.value = null;
    imported.value = false;
    statusText.value = "暂未选择文件";
    statusType.value = "";
    return;
  }

  selectedFile.value = file;
  imported.value = false;
  loading.value = true;
  statusText.value = "正在导入菜品数据...";
  statusType.value = "ready";

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE}/foods/upload`, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "导入失败");
    }

    imported.value = true;
    statusText.value = `导入成功，共导入 ${data.count} 个菜品，可以开始推荐`;
    statusType.value = "success";
  } catch (error) {
    console.error(error);
    imported.value = false;
    statusText.value = error.message || "导入失败，请检查后端是否启动";
    statusType.value = "error";
  } finally {
    loading.value = false;
  }
}

function goHome() {
  router.push("/");
}

function goRecommend() {
  router.push("/recommend");
}
</script>

<style scoped>
.upload-page {
  min-height: 100vh;
  padding: 64px 8%;
  background: linear-gradient(135deg, #eef6ff 0%, #f8fbff 100%);
  color: #0f172a;
}

.upload-card {
  max-width: 860px;
  margin: 0 auto;
  padding: 44px;
  border-radius: 32px;
  background: white;
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.1);
}

.tag {
  margin: 0 0 12px;
  color: #2563eb;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: 44px;
  line-height: 1.1;
}

.desc {
  margin: 18px 0 30px;
  color: #64748b;
  font-size: 16px;
  line-height: 1.8;
}

.upload-box {
  padding: 38px;
  border: 2px dashed #bfdbfe;
  border-radius: 26px;
  background: #f8fbff;
  text-align: center;
}

.choose-btn {
  color: white;
  background: linear-gradient(135deg, #2563eb, #0ea5e9);
  box-shadow: 0 14px 34px rgba(37, 99, 235, 0.24);
}

.file-name {
  margin: 18px 0 8px;
  color: #334155;
  font-weight: 800;
}

.status {
  margin: 0;
  color: #64748b;
}

.status.ready {
  color: #2563eb;
  font-weight: 800;
}

.status.success {
  color: #16a34a;
  font-weight: 800;
}

.status.error {
  color: #dc2626;
  font-weight: 800;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 30px;
}

button {
  border: none;
  border-radius: 999px;
  padding: 14px 24px;
  font-weight: 900;
  cursor: pointer;
  transition: 0.2s ease;
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
}

button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.secondary-btn {
  color: #2563eb;
  background: #eef4ff;
}

.recommend-btn {
  color: white;
  background: linear-gradient(135deg, #f97316, #fb923c);
  box-shadow: 0 14px 30px rgba(249, 115, 22, 0.24);
}

@media (max-width: 720px) {
  .upload-page {
    padding: 36px 5%;
  }

  .upload-card {
    padding: 30px 22px;
  }

  h1 {
    font-size: 34px;
  }

  .actions {
    flex-direction: column;
  }

  button {
    width: 100%;
  }
}
</style>