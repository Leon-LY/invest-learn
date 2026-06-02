/** Format ISO timestamp to relative time display */
export function formatTime(iso: string | undefined | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  const now = Date.now()
  const diff = now - d.getTime()
  const m = Math.floor(diff / 60000)
  const h = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  if (m < 1) return '刚刚'
  if (m < 60) return `${m}分钟前`
  if (h < 24) return `${h}小时前`
  if (days < 7) return `${days}天前`
  return `${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

/** Format ISO timestamp to date-time string */
export function formatDateTime(iso: string | undefined | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${d.getFullYear()}-${mm}-${dd} ${hh}:${mi}`
}
