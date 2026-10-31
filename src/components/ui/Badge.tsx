import React from 'react'
import { cn } from '@/lib/utils'

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'neutral' | 'success' | 'warning' | 'danger' | 'brass' | 'bronze'
}

export function Badge({
  className,
  variant = 'neutral',
  children,
  ...props
}: BadgeProps) {
  const variantStyles = {
    neutral: 'bg-warm-stone-light text-ink border-warm-stone',
    success: 'bg-garden-light text-garden-dark border-garden/30',
    warning: 'bg-warm-stone-light text-antique-brass-dark border-antique-brass/40',
    danger: 'bg-terracotta-light text-terracotta-dark border-terracotta/30',
    brass: 'bg-antique-brass-light/30 text-ink border-antique-brass/50',
    bronze: 'bg-bronze-light text-bronze-dark border-bronze/30',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 text-xs font-medium border rounded-md select-none tracking-wide',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  )
}
