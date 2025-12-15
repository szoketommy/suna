import React from 'react';
import { Globe } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WebsetsProgressBannerProps {
  isVisible: boolean;
  message?: string;
  progress?: {
    found: number;
    analyzed: number;
    completion: number;
    time_left?: number | null;
  };
}

export function WebsetsProgressBanner({
  isVisible,
  message,
  progress,
}: WebsetsProgressBannerProps) {
  if (!isVisible) return null;

  return (
    <div className="absolute top-0 left-0 right-0 z-10 bg-white dark:bg-zinc-950 border-b border-zinc-200 dark:border-zinc-800 px-4 py-3 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Globe className="w-5 h-5 text-zinc-900 dark:text-zinc-100 animate-pulse" />
            <div className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-zinc-900 dark:bg-zinc-100 animate-ping" />
          </div>
          <div>
            <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
              {message || "Searching the web..."}
            </div>
            {progress && (
              <div className="text-xs text-zinc-600 dark:text-zinc-400 font-medium mt-0.5">
                {progress.found} results found • {progress.completion}% complete
                {progress.time_left && ` • ~${progress.time_left}s remaining`}
              </div>
            )}
          </div>
        </div>
        {progress && (
          <div className="flex items-center gap-3">
            <div className="w-32 h-1.5 bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-zinc-900 dark:bg-zinc-100 rounded-full transition-all duration-500"
                style={{ width: `${progress.completion || 0}%` }}
              />
            </div>
            <span className="text-xs font-bold text-zinc-900 dark:text-zinc-100 w-10 tabular-nums">
              {progress.completion || 0}%
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
