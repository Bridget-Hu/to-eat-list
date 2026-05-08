import { requestJson } from "@/utils/api";

export function getOverviewStats() {
  return requestJson("/stats/overview");
}
