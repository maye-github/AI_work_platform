const encoder = new TextEncoder()

async function dayKey(): Promise<CryptoKey> {
  const day = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  const hash = await crypto.subtle.digest('SHA-256', encoder.encode(day))
  return crypto.subtle.importKey('raw', hash.slice(0, 16), { name: 'AES-CBC' }, false, ['encrypt'])
}

function base64Url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer)
  let text = ''
  bytes.forEach((byte) => { text += String.fromCharCode(byte) })
  return btoa(text).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

export async function encryptEmployeeCode(code: string): Promise<string> {
  const iv = new Uint8Array(16)
  const encrypted = await crypto.subtle.encrypt(
    { name: 'AES-CBC', iv },
    await dayKey(),
    encoder.encode(code),
  )
  return base64Url(encrypted)
}
