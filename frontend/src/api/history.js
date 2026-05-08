import { requestJson } from "@/utils/api";

function buildHistoryQuery({ limit = 500, startDate, endDate } = {}) {
  const params = new URLSearchParams();

  params.set("limit", String(limit));

  if (startDate) {
    params.set("start_date", startDate);
  }

  if (endDate) {
    params.set("end_date", endDate);
  }

  return params.toString();
}

export function listDailyRecords(options = {}) {
  const query = buildHistoryQuery(options);
  return requestJson(`/daily-records?${query}`);
}

export function clearDailyRecords() {
  return requestJson("/daily-records", {
    method: "DELETE"
  });
}

export function updateDailyRecordActualChoice(recordId, actualChoice) {
  return requestJson(`/daily-records/${recordId}/actual-choice`, {
    method: "PATCH",
    body: JSON.stringify({ actualChoice })
  });
}
