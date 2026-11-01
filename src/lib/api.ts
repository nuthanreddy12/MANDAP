import { supabase } from "./supabaseClient"

export async function getAccessToken(): Promise<string | null> {
  const isCustomerPath =
    typeof window !== "undefined" &&
    window.location.pathname.startsWith("/customer")

  if (isCustomerPath) {
    const custToken = localStorage.getItem("mandap_customer_token")
    if (custToken) return custToken
  }

  try {
    const { data, error } = await supabase.auth.getSession()
    if (!error && data.session?.access_token) {
      return data.session.access_token
    }
  } catch {
    // Supabase session lookup offline or not configured
  }

  return (
    localStorage.getItem("mandap_auth_token") ||
    localStorage.getItem("mandap_customer_token") ||
    null
  )
}

export async function fetchWithAuth(url: string, init?: RequestInit): Promise<Response> {
  let token: string | null = null
  if (url.includes("/customer/")) {
    token = localStorage.getItem("mandap_customer_token") || (await getAccessToken())
  } else {
    token = await getAccessToken()
  }

  const headers = new Headers(init?.headers || {})
  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }

  const response = await fetch(url, {
    ...init,
    headers,
  })

  if (response.status === 401) {
    const isCustomerScope =
      url.includes("/customer/") ||
      (typeof window !== "undefined" && window.location.pathname.startsWith("/customer"))

    if (isCustomerScope) {
      localStorage.removeItem("mandap_customer_token")
      localStorage.removeItem("mandap_customer_user")
      localStorage.removeItem("mandap_customer_wedding_id")
      if (
        typeof window !== "undefined" &&
        window.location.pathname !== "/customer/login" &&
        window.location.pathname !== "/customer/signup"
      ) {
        window.location.href = "/customer/login"
      }
    } else {
      try {
        await supabase.auth.signOut()
      } catch {
        // Ignore signout cleanup errors
      }
      localStorage.removeItem("mandap_auth_token")
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.href = "/login"
      }
    }
  }

  return response
}
