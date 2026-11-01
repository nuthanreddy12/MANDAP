import { createContext } from "react"
import type { Session, User } from "@supabase/supabase-js"

export interface AppUser {
  id: string
  auth_user_id: string | null
  name: string
  email: string
  role: "owner" | "planner" | "coordinator" | "finance_manager" | "customer" | string
  avatar_initials: string | null
}

export interface AuthContextType {
  session: Session | null
  user: User | null
  appUser: AppUser | null
  loading: boolean
  error: string | null
  signIn: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  signOut: () => Promise<void>
  refreshAppUser: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

