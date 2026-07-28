// API基础路径配置
// 开发环境使用 /api，生产环境使用 /stock-analysis/api
const API_BASE = import.meta.env.DEV ? '' : '/stock-analysis'

export function getApiUrl(path) {
  return `${API_BASE}${path}`
}

export async function fetchApi(path, options = {}) {
  const url = getApiUrl(path)
  const res = await fetch(url, options)
  return res.json()
}
