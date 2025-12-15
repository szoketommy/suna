import React from 'react';
import { Database, Globe, Sparkles } from 'lucide-react';

interface WebsetsEmptyStateProps {
  query?: string;
  isProcessing?: boolean;
}

export function WebsetsEmptyState({ query, isProcessing }: WebsetsEmptyStateProps) {
  if (isProcessing) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4">
        <div className="relative mb-4">
          <div className="w-16 h-16 rounded-full bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 flex items-center justify-center">
            <Globe className="w-8 h-8 text-zinc-900 dark:text-zinc-100 animate-pulse" />
          </div>
          <div className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-zinc-900 dark:bg-zinc-100 flex items-center justify-center">
            <Sparkles className="w-3 h-3 text-white dark:text-zinc-900" />
          </div>
        </div>
        <h3 className="text-lg font-bold text-zinc-900 dark:text-zinc-100 mb-2">
          Searching the web...
        </h3>
        <p className="text-sm text-zinc-600 dark:text-zinc-400 text-center max-w-md mb-3 font-medium">
          Scavenging the internet to compile your list. This can take 1-3 minutes depending on the number of results requested.
        </p>
        {query && (
          <div className="px-3 py-1.5 bg-white dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 rounded-md text-xs text-zinc-700 dark:text-zinc-300 max-w-sm truncate font-mono">
            "{query}"
          </div>
        )}
        <div className="mt-4 flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400 font-medium">
          <div className="w-2 h-2 rounded-full bg-zinc-900 dark:bg-zinc-100 animate-ping" />
          <span>AI agents are crawling and verifying results</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center h-full py-12 px-6 bg-white dark:bg-zinc-950">
      <div className="w-20 h-20 rounded-full flex items-center justify-center mb-6 bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
        <Database className="h-10 w-10 text-zinc-400 dark:text-zinc-500" />
      </div>
      <h3 className="text-xl font-bold mb-2 text-zinc-900 dark:text-zinc-100">
        No Results Found
      </h3>
      {query && (
        <div className="bg-white dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 rounded-lg p-4 w-full max-w-md text-center mb-4">
          <code className="text-sm font-mono text-zinc-700 dark:text-zinc-300 break-all">
            {query}
          </code>
        </div>
      )}
      <p className="text-sm text-zinc-600 dark:text-zinc-400 font-medium">
        Try refining your search criteria for better results
      </p>
    </div>
  );
}
