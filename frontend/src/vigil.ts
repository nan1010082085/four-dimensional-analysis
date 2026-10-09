/**
 * Vigil 浏览器监控 SDK 集成。
 * 提供前端性能与错误追踪；失败不阻断应用。
 * 未配置 VITE_VIGIL_TOKEN 时跳过初始化。
 */
import { createVigil, type BrowserVigil } from '@nan1010082085/vigil-browser'
import type { App } from 'vue'

let vigilInstance: BrowserVigil | null = null

/**
 * 解析 Vigil ingest 完整 URL。
 * @returns 完整 events 上报地址
 */
export function resolveVigilEndpoint(): string {
  const full = (import.meta.env.VITE_VIGIL_ENDPOINT as string | undefined)?.trim()
  if (full) {
    if (full.includes('/ingest/')) return full
    return `${full.replace(/\/+$/, '')}/ingest/v1/events`
  }
  const base = (import.meta.env.VITE_VIGIL_SERVER_URL as string | undefined)?.replace(/\/+$/, '')
  if (base) {
    if (base.includes('/ingest/')) return base
    return `${base}/ingest/v1/events`
  }
  return 'https://pyflow.icu/vigil-ingest/ingest/v1/events'
}

/**
 * 初始化 Vigil；无 token 时返回 null。
 * 本项目无 Vue Router，仅安装 vuePlugin。
 * @param app Vue 应用实例
 */
/**
 * 解析前端采样率（VITE_VIGIL_SAMPLE_RATE，默认 1）。
 */
function resolveSampleRate(): number {
  const raw = (import.meta.env.VITE_VIGIL_SAMPLE_RATE as string | undefined)?.trim()
  if (!raw) return 1
  const n = Number(raw)
  if (!Number.isFinite(n)) return 1
  return Math.min(1, Math.max(0, n))
}

export async function setupVigil(app: App): Promise<BrowserVigil | null> {
  if (vigilInstance) return vigilInstance

  const token = (import.meta.env.VITE_VIGIL_TOKEN as string | undefined)?.trim()
  if (!token) {
    console.warn('[vigil] skip: no VITE_VIGIL_TOKEN')
    return null
  }

  const endpoint = resolveVigilEndpoint()
  const environment = import.meta.env.MODE || 'development'

  console.log(`[vigil] Initializing four-dimensional-analysis (${environment}) → ${endpoint}`)

  try {
    vigilInstance = await createVigil({
      token,
      endpoint,
      service: { name: 'four-dimensional-analysis', env: environment },
      sampleRate: resolveSampleRate(),
    })
    app.use(vigilInstance.vuePlugin)
    installAutoClick()
    console.log('[vigil] Vue tracking installed')
    return vigilInstance
  } catch (err) {
    console.error('[vigil] Failed to initialize:', err)
    return null
  }
}

/**
 * 获取 Vigil 实例。
 */
export function getVigil(): BrowserVigil | null {
  return vigilInstance
}

/**
 * 按钮与链接点击自动上报，覆盖 trackClick 对应的 click 事件。
 */
function installAutoClick(): void {
  if (typeof document === 'undefined' || !vigilInstance) return
  document.addEventListener('click', (event) => {
    const raw = event.target
    if (!(raw instanceof Element) || !vigilInstance) return
    const el = raw.closest('button, a, [role="button"], input[type="submit"]')
    if (!el) return
    const target = el.getAttribute('data-vigil')
      || el.id
      || el.getAttribute('aria-label')
      || el.tagName.toLowerCase()
    vigilInstance.trackClick({ target: target.slice(0, 80), page: location.pathname })
  }, true)
}
