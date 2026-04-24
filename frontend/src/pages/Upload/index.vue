<template>
  <main class="upload-page">
    <section class="upload-card">
      <button class="back-btn" @click="$emit('go-home')">← 返回首页</button>

      <h1>上传菜品数据文档</h1>

      <p class="tip">
        请上传已经整理好的 txt / Word 文档，里面可以包含菜品、预算、口味、忌口、搭配等数据。
      </p>

      <input
        ref="fileInput"
        class="file-input"
        type="file"
        accept=".txt,.doc,.docx"
        @change="handleFileChange"
      />

      <div class="upload-box" @click="openFilePicker">
        <template v-if="!selectedFile">
          点击选择 txt / Word 文件
        </template>

        <template v-else>
          已选择：{{ selectedFile.name }}
        </template>
      </div>

      <div class="status-box">
        {{ statusText }}
      </div>

      <button class="upload-btn" :disabled="!selectedFile" @click="submitFile">
        确认上传
      </button>
    </section>
  </main>
</template>

<script setup>
import { ref, computed } from "vue";

const API_URL = "/api/meal-data/import";

const fileInput = ref(null);
const selectedFile = ref(null);
const status = ref("idle");

const statusText = computed(() => {
  if (status.value === "idle") return "待选择文件";
  if (status.value === "ready") return "文件已选择，等待上传";
  if (status.value === "uploading") return "正在上传到后端";
  if (status.value === "success") return "上传成功";
  if (status.value === "error") return "上传失败";
  return "待选择文件";
});

function openFilePicker() {
  fileInput.value.click();
}

function handleFileChange(event) {
  const file = event.target.files[0];

  if (!file) return;

  selectedFile.value = file;
  status.value = "ready";
}

async function submitFile() {
  if (!selectedFile.value) return;

  try {
    status.value = "uploading";

    const file = selectedFile.value;
    const ext = file.name.split(".").pop().toLowerCase();

    let parsedText = "";

    if (ext === "txt") {
      parsedText = await file.text();
    }

    const formData = new FormData();

    formData.append("file", file);
    formData.append("parsedText", parsedText);
    formData.append(
      "metadata",
      JSON.stringify({
        filename: file.name,
        fileType: ext,
        fileSize: file.size,
        needBackendParse: ext !== "txt",
        source: "campus-meal-import"
      })
    );

    const response = await fetch(API_URL, {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error("上传失败");
    }

    status.value = "success";
  } catch (error) {
    console.error(error);
    status.value = "error";
  }
}
</script>

<style scoped>
.upload-page {
  min-height: calc(100vh - 72px);
  padding: 60px 8%;
  display: flex;
  justify-content: center;
}

.upload-card {
  width: 100%;
  max-width: 760px;
  padding: 36px;
  border-radius: 28px;
  background: white;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
}

.back-btn {
  border: none;
  background: transparent;
  color: #2563eb;
  font-weight: 700;
  cursor: pointer;
  margin-bottom: 20px;
}

.upload-card h1 {
  margin: 0 0 16px;
  font-size: 34px;
}

.tip {
  color: #64748b;
  line-height: 1.8;
}

.file-input {
  display: none;
}

.upload-box {
  margin-top: 28px;
  height: 220px;
  border: 2px dashed #93c5fd;
  border-radius: 24px;
  background: #f8fbff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2563eb;
  font-size: 22px;
  font-weight: 800;
  cursor: pointer;
}

.status-box {
  margin-top: 18px;
  padding: 14px 18px;
  border-radius: 16px;
  background: #f1f5f9;
  color: #475569;
  font-weight: 700;
}

.upload-btn {
  width: 100%;
  margin-top: 18px;
  padding: 14px 28px;
  border: none;
  border-radius: 999px;
  background: #2563eb;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.upload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>