const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options)
  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    const detail = typeof payload === 'object' && payload?.detail
      ? payload.detail
      : typeof payload === 'string' && payload
        ? payload
        : `Request failed (${response.status})`

    throw new Error(detail)
  }

  return payload
}

export function getProducts() {
  return requestJson('/api/products')
}

export function queryDocumentation({ productId, version, question, topK = 3 }) {
  return requestJson('/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      product_id: productId,
      version,
      question,
      top_k: topK,
    }),
  })
}
