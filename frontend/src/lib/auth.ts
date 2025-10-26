/**
 * Authentication helper functions
 */

export interface User {
  id: number;
  email: string;
  name: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8432";

export function getSessionToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("ops_x_session");
}

export function getCurrentUser(): User | null {
  if (typeof window === "undefined") return null;
  const userStr = localStorage.getItem("ops_x_user");
  return userStr ? JSON.parse(userStr) : null;
}

export function isAuthenticated(): boolean {
  return !!getSessionToken();
}

export async function logout() {
  const token = getSessionToken();
  if (token) {
    try {
      await fetch(`${API_URL}/api/auth/logout?session_token=${token}`, {
        method: "POST",
      });
    } catch (err) {
      console.error("Logout error:", err);
    }
  }
  localStorage.removeItem("ops_x_session");
  localStorage.removeItem("ops_x_user");
  window.location.href = "/";
}

export async function checkAuth(): Promise<User | null> {
  const token = getSessionToken();
  if (!token) return null;

  try {
    const res = await fetch(`${API_URL}/api/auth/me?session_token=${token}`);
    const data = await res.json();

    if (data.success) {
      return data.user;
    }
    return null;
  } catch {
    return null;
  }
}

export async function signUp(
  email: string,
  name: string
): Promise<{ success: boolean; message: string }> {
  try {
    const res = await fetch(`${API_URL}/api/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, name }),
    });

    const data = await res.json();
    return {
      success: data.success,
      message: data.message || "OTP sent to your email",
    };
  } catch (err) {
    return {
      success: false,
      message: "Network error. Please try again.",
    };
  }
}

export async function verifyOTP(
  email: string,
  otp: string
): Promise<{
  success: boolean;
  user?: User;
  session_token?: string;
  message?: string;
}> {
  try {
    const res = await fetch(`${API_URL}/api/auth/verify-otp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, otp }),
    });

    const data = await res.json();

    if (data.success) {
      // Store session
      localStorage.setItem("ops_x_session", data.session_token);
      localStorage.setItem(
        "ops_x_user",
        JSON.stringify({
          id: data.user_id,
          email: data.email,
          name: data.name,
        })
      );

      return {
        success: true,
        user: {
          id: data.user_id,
          email: data.email,
          name: data.name,
        },
        session_token: data.session_token,
      };
    }

    return {
      success: false,
      message: data.message || "Invalid OTP",
    };
  } catch (err) {
    return {
      success: false,
      message: "Network error. Please try again.",
    };
  }
}
