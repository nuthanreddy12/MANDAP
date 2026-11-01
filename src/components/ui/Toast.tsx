import React from "react"
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react"

export interface ToastMessage {
  id: string
  type: "success" | "error" | "info"
  message: string
}

interface ToastContainerProps {
  toasts: ToastMessage[]
  onDismiss: (id: string) => void
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto flex items-start gap-3 p-3.5 rounded-lg border shadow-xl backdrop-blur-md transition-all animate-in slide-in-from-bottom-2 ${
            toast.type === "success"
              ? "bg-[#0E2A1D]/90 border-emerald-500/30 text-emerald-200"
              : toast.type === "error"
              ? "bg-[#2F1116]/90 border-rose-500/30 text-rose-200"
              : "bg-[#131926]/90 border-slate-700 text-slate-200"
          }`}
        >
          {toast.type === "success" && <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />}
          {toast.type === "error" && <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />}
          {toast.type === "info" && <Info className="w-5 h-5 text-sky-400 shrink-0 mt-0.5" />}
          <div className="flex-1 text-xs font-medium leading-relaxed">{toast.message}</div>
          <button
            onClick={() => onDismiss(toast.id)}
            className="text-slate-400 hover:text-white shrink-0 p-0.5"
            aria-label="Dismiss toast"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  )
}
