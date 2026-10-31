import React from 'react'
import { cn } from '@/lib/utils'

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'muted' | 'elevated' | 'warm'
}

export function Card({
  className,
  variant = 'default',
  children,
  ...props
}: CardProps) {
  const variantStyles = {
    default: 'bg-ivory-card border border-warm-stone shadow-[0_2px_8px_rgba(44,37,35,0.03)]',
    muted: 'bg-ivory-warm border border-warm-stone/80',
    elevated: 'bg-ivory-card border border-warm-stone/90 shadow-[0_8px_24px_rgba(44,37,35,0.06)]',
    warm: 'bg-warm-stone-light/50 border border-warm-stone shadow-[0_2px_6px_rgba(44,37,35,0.02)]',
  }

  return (
    <div
      className={cn('rounded-lg transition-all text-ink', variantStyles[variant], className)}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('px-6 py-5 border-b border-warm-stone/60', className)}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardTitle({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn('font-serif text-xl tracking-tight text-ink font-semibold', className)}
      {...props}
    >
      {children}
    </h3>
  )
}

export function CardDescription({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn('text-xs text-ink-muted mt-1 leading-relaxed', className)}
      {...props}
    >
      {children}
    </p>
  )
}

export function CardContent({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('p-6', className)} {...props}>
      {children}
    </div>
  )
}

export function CardFooter({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('px-6 py-4 border-t border-warm-stone/60 flex items-center justify-between', className)}
      {...props}
    >
      {children}
    </div>
  )
}
