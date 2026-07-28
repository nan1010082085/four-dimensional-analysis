// API基础路径配置
// 开发环境使用 /api，生产环境使用 /stock-analysis/api
const API_BASE = import.meta.env.DEV ? '' : '/stock-analysis'

export function getApiUrl(path) {
  // 确保路径以 /api 开头
  const apiPath = path.startsWith('/api') ? path : `/api${path}`
  return `${API_BASE}${apiPath}`
}

export async function fetchApi(path, options = {}) {
  const url = getApiUrl(path)
  try {
    const res = await fetch(url, options)
    const text = await res.text()
    // 检查是否返回了HTML
    if (text.startsWith('<!DOCTYPE') || text.startsWith('<html')) {
      throw new Error('API返回了HTML而非JSON，路径可能有误')
    }
    return JSON.parse(text)
  } catch (e) {
    console.error('API请求失败:', url, e)
    throw e
  }
}
