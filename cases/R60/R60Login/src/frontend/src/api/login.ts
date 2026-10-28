const baseUrl = import.meta.env.VITE_API_BASE ?? 'http://localhost:8080'

async function post<T>(path: string, params: Record<string, unknown>): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ params }),
  })
  return (await response.json()) as T
}

export const initLogin = () => post('/R60Login/init', {})
export const doLogin = (params: Record<string, unknown>) => post('/R60Login/login', params)
export const generateUrl = (params: Record<string, unknown>) => post('/R60Login/generateUrl', params)
