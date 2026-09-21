"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createWorkspace } from "@/lib/api";
import { BookOpen, Building2, ArrowRight } from "lucide-react";

export default function OnboardingPage() {
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [slugModified, setSlugModified] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleNameChange = (val: string) => {
    setName(val);
    if (!slugModified) {
      const generatedSlug = val
        .toLowerCase()
        .trim()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");
      setSlug(generatedSlug);
    }
  };

  const handleCreateWorkspace = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim() || !slug.trim()) {
      setError("Please provide a valid workspace name and slug.");
      return;
    }

    setLoading(true);

    const { data, error: apiErr } = await createWorkspace({
      name: name.trim(),
      slug: slug.trim(),
    });

    if (apiErr || !data) {
      setError(apiErr || "Failed to create workspace. Please try again.");
      setLoading(false);
      return;
    }

    router.push("/");
    router.refresh();
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8 rounded-2xl border border-border bg-surface p-8 shadow-xl">
        <div className="flex flex-col items-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-border bg-surface-muted text-accent">
            <Building2 className="h-6 w-6" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-text-primary">
            Create your workspace
          </h2>
          <p className="mt-2 text-center text-sm text-text-muted">
            Set up your organization workspace to start managing and querying your documents securely.
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleCreateWorkspace}>
          {error && (
            <div className="rounded-md bg-danger/10 p-4 border border-danger/20 text-sm text-danger">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="workspace-name" className="block text-xs font-semibold uppercase tracking-wider text-text-muted mb-1.5">
                Workspace Name
              </label>
              <input
                id="workspace-name"
                name="name"
                type="text"
                required
                value={name}
                onChange={(e) => handleNameChange(e.target.value)}
                className="relative block w-full rounded-md border-0 bg-surface-muted py-2.5 px-3 text-text-primary ring-1 ring-inset ring-border placeholder:text-text-muted focus:ring-2 focus:ring-inset focus:ring-accent sm:text-sm sm:leading-6"
                placeholder="e.g. Acme Health Corp"
              />
            </div>

            <div>
              <label htmlFor="workspace-slug" className="block text-xs font-semibold uppercase tracking-wider text-text-muted mb-1.5">
                Workspace Slug (URL identifier)
              </label>
              <input
                id="workspace-slug"
                name="slug"
                type="text"
                required
                value={slug}
                onChange={(e) => {
                  setSlug(e.target.value);
                  setSlugModified(true);
                }}
                className="relative block w-full rounded-md border-0 bg-surface-muted py-2.5 px-3 text-text-primary ring-1 ring-inset ring-border placeholder:text-text-muted focus:ring-2 focus:ring-inset focus:ring-accent sm:text-sm sm:leading-6 font-mono text-xs"
                placeholder="acme-health-corp"
              />
              <p className="mt-1 text-xs text-text-muted">
                Letters, numbers, and hyphens only.
              </p>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-md bg-accent px-3 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-accent-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span>{loading ? "Creating workspace..." : "Continue to Dashboard"}</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
