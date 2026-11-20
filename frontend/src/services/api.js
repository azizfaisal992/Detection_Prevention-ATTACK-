const BRIDGE_URL = 'http://127.0.0.1:8080'

async function request(path, options = {}) {
  const response = await fetch(`${BRIDGE_URL}${path}`, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...options.headers,
    },
  })
  let payload
  try {
    payload = await response.json()
  } catch {
    throw new Error('The backend returned an invalid response')
  }
  if (!response.ok) {
    const error = new Error(payload.message || 'Backend request failed')
    error.code = payload.code
    throw error
  }
  return payload
}

export async function getServerStatus() {
  return request('/api/status')
}

export async function login(username, password) {
  return request('/api/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export async function getOwnBalance(sessionToken) {
  return request('/api/balance', {
    method: 'POST',
    body: JSON.stringify({ session_token: sessionToken }),
  })
}

export async function logout(sessionToken) {
  return request('/api/logout', {
    method: 'POST',
    body: JSON.stringify({ session_token: sessionToken }),
  })
}

