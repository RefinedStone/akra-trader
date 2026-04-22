import { apiBase } from "../controlRoomDefinitions";

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers,
  });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const errorPayload = await response.json() as { detail?: unknown };
      if (typeof errorPayload.detail === "string" && errorPayload.detail.trim()) {
        detail = `${response.status} ${errorPayload.detail}`;
      }
    } catch {
      // Ignore malformed error payloads and fall back to the HTTP status text.
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}
