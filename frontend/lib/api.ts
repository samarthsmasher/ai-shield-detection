/**
 * Shared API utility for all detection pages.
 * Handles Render free-tier cold starts (50-90s wake-up time).
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

/**
 * Wake up the Render backend if it's sleeping.
 * Pings /api/health with retries until it responds.
 * Returns true if backend is up, false if unreachable after timeout.
 */
export async function wakeBackend(
  onStatus?: (msg: string) => void,
  maxWaitMs = 180_000
): Promise<boolean> {
  const start = Date.now();
  let attempt = 0;

  while (Date.now() - start < maxWaitMs) {
    attempt++;
    try {
      const controller = new AbortController();
      const tid = setTimeout(() => controller.abort(), 8_000);

      const res = await fetch(`${API_BASE}/api/health`, {
        signal: controller.signal,
        cache:  "no-store",
      });
      clearTimeout(tid);

      if (res.ok) {
        onStatus?.("Backend ready ✓");
        return true;
      } else {
        throw new Error(`Server returned ${res.status}`);
      }
    } catch {
      const elapsed = Math.round((Date.now() - start) / 1000);
      onStatus?.(
        attempt === 1
          ? "Waking up server… this may take ~2-3 mins on first use"
          : `Still waking up… ${elapsed}s elapsed`
      );
      await sleep(4_000);
    }
  }
  return false;
}

/**
 * fetch() wrapper with a configurable timeout.
 * Throws a user-friendly error on timeout.
 */
export async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeoutMs = 120_000
): Promise<Response> {
  const controller = new AbortController();
  const tid = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(tid);
    return res;
  } catch (err: unknown) {
    clearTimeout(tid);
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("Request timed out. The server may be waking up — please try again in 30 seconds.");
    }
    throw err;
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
