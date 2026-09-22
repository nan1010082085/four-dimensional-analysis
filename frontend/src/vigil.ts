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
    })
    app.use(vigilInstance.vuePlugin)
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
