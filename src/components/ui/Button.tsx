import React from 'react'
import { cn } from '@/lib/utils'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'bronze'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      disabled,
      children,
      type = 'button',
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'inline-flex items-center justify-center font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-antique-brass focus-visible:ring-offset-2 focus-visible:ring-offset-ivory disabled:pointer-events-none disabled:opacity-50 select-none'

    const variantStyles = {
      primary:
        'bg-ink text-ivory hover:bg-ink/90 active:bg-ink shadow-xs',
      bronze:
        'bg-bronze text-ivory hover:bg-bronze-dark active:bg-bronze-dark shadow-xs',
      secondary:
        'bg-warm-stone-light text-ink hover:bg-warm-stone active:bg-warm-stone-dark/40 border border-warm-stone',
      outline:
        'border border-bronze/30 text-ink bg-transparent hover:bg-warm-stone-light/60 active:bg-warm-stone',
      ghost:
        'text-ink hover:bg-warm-stone-light/70 active:bg-warm-stone',
      danger:
        'bg-terracotta text-ivory hover:bg-terracotta-dark active:bg-terracotta-dark/90',
    }

    const sizeStyles = {
      sm: 'min-h-[38px] px-3.5 py-1.5 text-xs rounded-md gap-1.5',
      md: 'min-h-[44px] px-5 py-2.5 text-sm rounded-md gap-2',
      lg: 'min-h-[50px] px-6 py-3 text-base rounded-md gap-2.5',
    }

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
        {...props}
      >
        {isLoading ? (
          <span
            className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
            role="status"
            aria-label="Loading"
          />
        ) : (
          leftIcon && <span className="inline-flex shrink-0">{leftIcon}</span>
        )}
        <span>{children}</span>
        {!isLoading && rightIcon && (
          <span className="inline-flex shrink-0">{rightIcon}</span>
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'
