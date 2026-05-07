export const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function requestJson(path, options = {}) {
  const { headers = {}, body, ...rest } = options;
  const requestHeaders = {
    Accept: "application/json",
    ...headers
  };

  const requestOptions = {
    ...rest,
    headers: requestHeaders
  };

  if (body !== undefined) {
    requestOptions.body = body;

    if (!(body instanceof FormData) && !requestHeaders["Content-Type"]) {
      requestHeaders["Content-Type"] = "application/json";
    }
  }

  const response = await fetch(`${API_BASE}${path}`, requestOptions);

  let data;

  try {
    const raw = await response.text();
    data = raw ? JSON.parse(raw) : null;
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new Error(data?.detail || data?.message || "请求失败，请稍后重试。");
  }

  return data;
}
