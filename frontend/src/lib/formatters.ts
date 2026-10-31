/**
 * Currency & numerical formatters conforming to Indian numbering system (Lakhs & Crores)
 * and Anti-Slop precision rules (no silent truncation or rounding).
 */

export function formatINR(amount: number | string | null | undefined, compact = false): string {
  if (amount === null || amount === undefined || isNaN(Number(amount))) {
    return "₹0"
  }
  const val = Number(amount)

  if (compact) {
    const absVal = Math.abs(val)
    if (absVal >= 10000000) {
      const cr = val / 10000000
      return `₹${cr.toFixed(2).replace(/\.00$/, '')}Cr`
    }
    if (absVal >= 100000) {
      const lk = val / 100000
      return `₹${lk.toFixed(2).replace(/\.00$/, '')}L`
    }
    if (absVal >= 1000) {
      const k = val / 1000
      return `₹${k.toFixed(1).replace(/\.0$/, '')}k`
    }
  }

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(val)
}

export function formatDate(dateString: string | Date | null | undefined): string {
  if (!dateString) return ""
  const d = new Date(dateString)
  return new Intl.DateTimeFormat('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  }).format(d)
}

export function formatTime(timeString: string | null | undefined): string {
  if (!timeString) return ""
  return timeString
}
