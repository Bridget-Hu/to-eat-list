import { requestJson } from "@/utils/api";

export const foodCategoryOptions = [
  { label: "主食", value: "主食" },
  { label: "奶茶", value: "奶茶" },
  { label: "小吃", value: "小吃" },
  { label: "水果", value: "水果" },
  { label: "其他", value: "其他" }
];

export function splitTagText(value) {
  if (!value) {
    return [];
  }

  return String(value)
    .replace(/，/g, "、")
    .replace(/,/g, "、")
    .split("、")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function listFoods() {
  return requestJson("/foods");
}

export function createFood(payload) {
  return requestJson("/foods", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateFood(foodId, payload) {
  return requestJson(`/foods/${foodId}`, {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}

export function deleteFood(foodId) {
  return requestJson(`/foods/${foodId}`, {
    method: "DELETE"
  });
}

export function uploadFoodFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  return requestJson("/foods/upload", {
    method: "POST",
    body: formData
  });
}
