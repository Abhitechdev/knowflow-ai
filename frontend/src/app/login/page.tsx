"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";
import { BookOpen, ShieldCheck, ArrowRight, ArrowLeft, Lock, CheckCircle2 } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const supabase = createClient();
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }

    router.push("/");
    router.refresh();
  };

  return (
    <div className="flex min-h-screen flex-col justify-center bg-background px-4 py-12 sm:px-6 lg:px-8 selection:bg-accent/20">
      <div className="sm:mx-auto sm:w-full sm:max-w-md space-y-6">
        {/* Navigation back to Home */}
        <div className="text-center">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-text-muted hover:text-text-primary transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" /> Back to Product Overview
          </Link>
        </div>

        {/* Card Container */}
        <div className="rounded-2xl border border-border bg-surface p-8 sm:p-10 shadow-2xl space-y-6">
          <div className="flex flex-col items-center text-center space-y-3">
            <Link href="/" className="flex h-12 w-12 items-center justify-center rounded-xl border border-border bg-surface-muted text-accent shadow-sm hover:scale-105 transition-transform">
              <BookOpen className="h-6 w-6" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-text-primary">
                Sign in to KnowFlow AI
              </h1>
              <p className="mt-1.5 text-xs text-text-muted">
                Enterprise Knowledge & SOP Intelligence Assistant
              </p>
            </div>
          </div>

          {/* Registration Prompt */}
          <div className="rounded-lg border border-accent/20 bg-accent/5 p-3 text-center">
            <p className="text-xs text-text-secondary">
              Don&apos;t have an account?{" "}
              <Link href="/register" className="font-semibold text-accent hover:underline inline-flex items-center gap-0.5">
                Register a new workspace <ArrowRight className="h-3 w-3" />
              </Link>
            </p>
          </div>

          <form className="space-y-4" onSubmit={handleLogin}>
            {error && (
              <div className="rounded-lg bg-danger/10 p-3.5 border border-danger/20 text-xs text-danger leading-relaxed">
                {error}
              </div>
            )}

            <div className="space-y-1.5">
              <label htmlFor="email-address" className="block text-xs font-medium text-text-primary">
                Corporate Email Address
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="block w-full rounded-lg border border-border bg-surface-muted px-3.5 py-2.5 text-xs text-text-primary placeholder:text-text-muted focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
                placeholder="you@company.com"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="block text-xs font-medium text-text-primary">
                  Password
                </label>
                <Link href="/reset-password" className="text-[11px] font-medium text-accent hover:underline">
                  Forgot password?
                </Link>
              </div>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="block w-full rounded-lg border border-border bg-surface-muted px-3.5 py-2.5 text-xs text-text-primary placeholder:text-text-muted focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
                placeholder="••••••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex w-full justify-center rounded-lg bg-accent px-4 py-2.5 text-xs font-semibold text-accent-foreground shadow-sm hover:bg-accent/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? "Verifying credentials..." : "Sign in to Workspace"}
            </button>
          </form>

          {/* Trust & DPDP Footer */}
          <div className="border-t border-border pt-4 text-center">
            <Link
              href="/security"
              className="inline-flex items-center gap-1.5 text-[11px] text-text-muted hover:text-text-primary transition-colors"
            >
              <ShieldCheck className="h-3.5 w-3.5 text-success" /> DPDPA 2023 & GDPR Aligned • Zero AI Training
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
