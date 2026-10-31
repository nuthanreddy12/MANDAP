import React, { createContext, useContext, useEffect, useState, useCallback } from "react"
import type { Session, User } from "@supabase/supabase-js"
import { supabase } from "./supabaseClient"

export interface AppUser {
  id: string
  auth_user_id: string | null
  name: string
  email: string
  role: "owner" | "planner" | "coordinator" | "finance_manager" | string
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

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<Session | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [appUser, setAppUser] = useState<AppUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchAppUserProfile = useCallback(async (token: string): Promise<AppUser | null> => {
    try {
      const res = await fetch("/api/v1/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      if (!res.ok) {
        if (res.status === 403) {
          setError("We couldn't find an account associated with this email. Check your details or contact your agency administrator.")
        }
        return null
      }
      const data: AppUser = await res.json()
      setAppUser(data)
      setError(null)
      return data
    } catch (err) {
      console.error("Failed to load application profile:", err)
      return null
    }
  }, [])

  const refreshAppUser = useCallback(async () => {
    if (session?.access_token) {
      await fetchAppUserProfile(session.access_token)
    }
  }, [session, fetchAppUserProfile])

  useEffect(() => {
    // 1. Initial session restoration
    supabase.auth.getSession().then(({ data: { session: initialSession } }) => {
      setSession(initialSession)
      setUser(initialSession?.user ?? null)
      if (initialSession?.access_token) {
        fetchAppUserProfile(initialSession.access_token).finally(() => setLoading(false))
      } else {
        setLoading(false)
      }
    }).catch(() => {
      setLoading(false)
    })

    // 2. Auth state changes listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, currentSession) => {
      setSession(currentSession)
      setUser(currentSession?.user ?? null)
      if (currentSession?.access_token) {
        await fetchAppUserProfile(currentSession.access_token)
      } else {
        setAppUser(null)
      }
      setLoading(false)
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [fetchAppUserProfile])

  const signIn = async (email: string, password: string) => {
    setError(null)
    try {
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (signInError) {
        setError("Invalid email or password. Please verify your credentials and try again.")
        return {
          success: false,
          error: "Invalid email or password. Please verify your credentials and try again.",
        }
      }

      if (data.session?.access_token) {
        const profile = await fetchAppUserProfile(data.session.access_token)
        if (!profile) {
          return {
            success: false,
            error: "We couldn't find an account associated with this email. Check your details or contact your agency administrator.",
          }
        }
      }

      return { success: true }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Authentication failed"
      setError(message)
      return { success: false, error: message }
    }
  }

  const signOut = async () => {
    try {
      await supabase.auth.signOut()
    } finally {
      setSession(null)
      setUser(null)
      setAppUser(null)
      setError(null)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        session,
        user,
        appUser,
        loading,
        error,
        signIn,
        signOut,
        refreshAppUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
