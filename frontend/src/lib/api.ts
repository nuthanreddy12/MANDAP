import { supabase } from "./supabaseClient"

export async function getAccessToken(): Promise<string | null> {
  try {
    const { data, error } = await supabase.auth.getSession()
    if (!error && data.session?.access_token) {
      return data.session.access_token
    }
  } catch {
    // Supabase session lookup failed or offline
  }
  return (
    localStorage.getItem("mandap_customer_token") ||
    localStorage.getItem("mandap_auth_token") ||
    null
  )
}

export async function fetchWithAuth(url: string, init?: RequestInit): Promise<Response> {
  const token = await getAccessToken()
  const headers = new Headers(init?.headers || {})

  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }

  const response = await fetch(url, {
    ...init,
    headers,
  })

  if (response.status === 401) {
    try {
      await supabase.auth.signOut()
    } catch {
      // Ignore signout cleanup errors
    }
    localStorage.removeItem("mandap_customer_token")
    localStorage.removeItem("mandap_customer_user")
    if (window.location.pathname.startsWith("/customer/")) {
      if (window.location.pathname !== "/customer/login" && window.location.pathname !== "/customer/signup") {
        window.location.href = "/customer/login"
      }
    } else if (window.location.pathname !== "/login") {
      window.location.href = "/login"
    }
  }

  return response
}
