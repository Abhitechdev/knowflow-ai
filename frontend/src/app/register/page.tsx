"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";
import { BookOpen } from "lucide-react";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    const supabase = createClient();
    const siteUrl = typeof window !== "undefined" && window.location.origin
      ? window.location.origin
      : (process.env.NEXT_PUBLIC_SITE_URL || "https://knowflow-ai-pied.vercel.app");
    const emailRedirectTo = `${siteUrl.replace(/\/$/, "")}/auth/callback`;

    const { error, data } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo,
      },
    });

    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }

    if (data.session) {
      router.push("/");
      router.refresh();
    } else {
      setSuccess("Check your email for the confirmation link.");
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8 rounded-2xl border border-border bg-surface p-8 shadow-xl">
        <div className="flex flex-col items-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-border bg-surface-muted text-accent">
            <BookOpen className="h-6 w-6" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-text-primary">
            Create an account
          </h2>
          <p className="mt-2 text-center text-sm text-text-muted">
            Or{" "}
            <Link href="/login" className="font-medium text-accent hover:underline">
              sign in to your existing account
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleRegister}>
          {error && (
            <div className="rounded-md bg-danger/10 p-4 border border-danger/20 text-sm text-danger">
              {error}
            </div>
          )}
          {success && (
            <div className="rounded-md bg-success/10 p-4 border border-success/20 text-sm text-success">
              {success}
            </div>
          )}
          <div className="space-y-4 rounded-md shadow-sm">
            <div>
              <label htmlFor="email-address" className="sr-only">
                Email address
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="relative block w-full rounded-md border-0 bg-surface-muted py-2.5 px-3 text-text-primary ring-1 ring-inset ring-border placeholder:text-text-muted focus:z-10 focus:ring-2 focus:ring-inset focus:ring-accent sm:text-sm sm:leading-6"
                placeholder="Email address"
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="relative block w-full rounded-md border-0 bg-surface-muted py-2.5 px-3 text-text-primary ring-1 ring-inset ring-border placeholder:text-text-muted focus:z-10 focus:ring-2 focus:ring-inset focus:ring-accent sm:text-sm sm:leading-6"
                placeholder="Password"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="flex w-full justify-center rounded-md bg-accent px-3 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-accent-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Creating account..." : "Create account"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
