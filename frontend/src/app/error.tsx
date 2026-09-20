"use client";

import { useEffect } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error("Global Error Boundary caught:", error);
  }, [error]);

  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center space-y-4 p-8 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-danger/10 text-danger mb-2">
        <AlertCircle className="h-8 w-8" />
      </div>
      <h2 className="text-xl font-semibold tracking-tight text-text-primary">Something went wrong</h2>
      <p className="text-sm text-text-muted max-w-md">
        {error.message || "An unexpected error occurred while rendering this page."}
      </p>
      <div className="pt-4">
        <button
          onClick={() => reset()}
          className="inline-flex items-center space-x-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Try again</span>
        </button>
      </div>
    </div>
  );
}
