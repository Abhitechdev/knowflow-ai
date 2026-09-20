"use client";

import { Toaster } from "sonner";

export function ToastProvider() {
  return (
    <Toaster 
      theme="dark" 
      position="bottom-right" 
      toastOptions={{
        className: 'border-border bg-surface text-text-primary rounded-md shadow-lg',
      }}
    />
  );
}
