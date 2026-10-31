export function FloralFlourish({ className = 'w-12 h-12 text-antique-brass/40' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 100 100"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {/* Central stem */}
      <path d="M50 95 C 48 65, 52 35, 50 5" />
      {/* Delicate leaves / petals */}
      <path d="M50 75 C 35 70, 30 55, 48 62" />
      <path d="M50 60 C 65 55, 70 40, 52 47" />
      <path d="M50 45 C 35 40, 30 25, 48 32" />
      <path d="M50 30 C 65 25, 70 10, 52 17" />
      {/* Blossom top */}
      <circle cx="50" cy="8" r="3" fill="currentColor" />
    </svg>
  )
}

export function FloralCorner({ className = 'w-16 h-16 text-antique-brass/30' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 80 80"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M 5 5 L 45 5 C 60 5, 75 20, 75 35" />
      <path d="M 5 5 L 5 45 C 5 60, 20 75, 35 75" />
      <path d="M 12 12 Q 35 25 45 15 Q 25 35 12 12 Z" fill="currentColor" fillOpacity="0.1" />
      <circle cx="45" cy="15" r="2" fill="currentColor" />
      <circle cx="15" cy="45" r="2" fill="currentColor" />
    </svg>
  )
}

export function BotanicalDivider({ className = 'w-32 h-6 text-antique-brass/40' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 200 30"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <line x1="10" y1="15" x2="75" y2="15" />
      <path d="M 85 15 C 90 9, 95 9, 100 15 C 105 21, 110 21, 115 15" />
      <circle cx="100" cy="15" r="3" fill="currentColor" />
      <line x1="125" y1="15" x2="190" y2="15" />
    </svg>
  )
}
