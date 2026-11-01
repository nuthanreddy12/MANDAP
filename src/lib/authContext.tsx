import React, { useEffect, useState, useCallback } from "react"
import type { Session, User } from "@supabase/supabase-js"
import { supabase } from "./supabaseClient"
import { AuthContext, type AppUser } from "./AuthContextDef"

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
          setError("We could not find an account associated with this email. Check your details or contact your agency administrator.")
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
    const token = session?.access_token || localStorage.getItem("mandap_auth_token")
    if (token) {
      await fetchAppUserProfile(token)
    }
  }, [session, fetchAppUserProfile])

  useEffect(() => {
    let mounted = true

    const restoreSession = async () => {
      try {
        const { data: { session: initialSession } } = await supabase.auth.getSession()
        if (!mounted) return

        if (initialSession?.access_token) {
          setSession(initialSession)
          setUser(initialSession.user ?? null)
          await fetchAppUserProfile(initialSession.access_token)
          if (mounted) setLoading(false)
          return
        }
      } catch {
        // Supabase lookup offline or not configured
      }

      // Check fallback local staff token
      const localStaffToken = localStorage.getItem("mandap_auth_token")
      if (localStaffToken && mounted) {
        const profile = await fetchAppUserProfile(localStaffToken)
        if (!profile && mounted) {
          localStorage.removeItem("mandap_auth_token")
        }
      }

      if (mounted) {
        setLoading(false)
      }
    }

    restoreSession()

    // Auth state changes listener for Supabase
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, currentSession) => {
      if (!mounted) return
      setSession(currentSession)
      setUser(currentSession?.user ?? null)
      if (currentSession?.access_token) {
        await fetchAppUserProfile(currentSession.access_token)
      } else if (!localStorage.getItem("mandap_auth_token")) {
        setAppUser(null)
      }
      setLoading(false)
    })

    return () => {
      mounted = false
      subscription.unsubscribe()
    }
  }, [fetchAppUserProfile])

  const signIn = async (email: string, password: string) => {
    setError(null)
    try {
      let token: string | null = null

      // 1. Try Supabase Auth first
      try {
        const { data, error: sbError } = await supabase.auth.signInWithPassword({
          email: email.trim().toLowerCase(),
          password,
        })
        if (!sbError && data.session?.access_token) {
          token = data.session.access_token
          setSession(data.session)
          setUser(data.user)
        }
      } catch {
        // Supabase Auth call failed or offline, fall through to backend
      }

      // 2. Fall back to backend staff login endpoint
      if (!token) {
        const res = await fetch("/api/v1/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
        })

        if (res.ok) {
          const authData = await res.json()
          if (authData.token && typeof authData.token === "string") {
            token = authData.token
            localStorage.setItem("mandap_auth_token", authData.token)
          }
        } else {
          const errData = await res.json().catch(() => ({}))
          const msg = errData.detail || "Invalid email or password. Please verify your credentials and try again."
          setError(msg)
          return { success: false, error: msg }
        }
      }

      if (token) {
        const profile = await fetchAppUserProfile(token)
        if (!profile) {
          return {
            success: false,
            error: "We could not find an account associated with this email. Check your details or contact your agency administrator.",
          }
        }
        localStorage.setItem("mandap_auth_token", token)
        return { success: true }
      }

      const defaultMsg = "Invalid email or password. Please verify your credentials and try again."
      setError(defaultMsg)
      return { success: false, error: defaultMsg }
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
      localStorage.removeItem("mandap_customer_token")
      localStorage.removeItem("mandap_customer_user")
      localStorage.removeItem("mandap_customer_wedding_id")
      localStorage.removeItem("mandap_auth_token")
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
