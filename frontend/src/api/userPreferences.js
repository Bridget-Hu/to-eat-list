import { requestJson } from "@/utils/api";

export function saveUserPreference(payload) {
  return requestJson("/user/preferences", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getLatestUserPreference() {
  return requestJson("/user/preferences/latest");
}
