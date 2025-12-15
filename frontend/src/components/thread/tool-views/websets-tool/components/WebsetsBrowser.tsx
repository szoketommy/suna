import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from "@/components/ui/scroll-area";
import { Database } from 'lucide-react';
import { cn } from '@/lib/utils';
import { WebsetData, WebsetItem } from '../types';
import { WebsetsProgressBanner } from './WebsetsProgressBanner';
import { WebsetsEmptyState } from './WebsetsEmptyState';
import { WebsetsTable } from './WebsetsTable';
import { WebsetsToolbar } from './WebsetsToolbar';

interface WebsetsBrowserProps {
  data: WebsetData;
  isStreaming: boolean;
  isPolling: boolean;
  items: WebsetItem[];
  onToggleExpand: (itemId: string) => void;
  expandedRows: Set<string>;
  searchFilter: string;
  onSearchChange: (value: string) => void;
}

export function WebsetsBrowser({
  data,
  isStreaming,
  isPolling,
  items,
  onToggleExpand,
  expandedRows,
  searchFilter,
  onSearchChange,
}: WebsetsBrowserProps) {
  // Extract all unique criteria from items' evaluations
  const allCriteria = useMemo(() => {
    const criteriaSet = new Set<string>();
    items.forEach(item => {
      item.evaluations?.forEach(evaluation => {
        if (evaluation.criterion) {
          criteriaSet.add(evaluation.criterion);
        }
      });
    });
    return Array.from(criteriaSet);
  }, [items]);

  const filteredItems = useMemo(() => {
    if (!searchFilter) return items;
    const filter = searchFilter.toLowerCase();
    return items.filter(item => 
      item.name?.toLowerCase().includes(filter) ||
      item.title?.toLowerCase().includes(filter) ||
      item.description?.toLowerCase().includes(filter) ||
      item.location?.toLowerCase().includes(filter) ||
      item.industry?.toLowerCase().includes(filter)
    );
  }, [items, searchFilter]);

  const showProgressBanner = data.is_processing || isPolling || (isStreaming && !data.is_complete);
  const showEmptyState = (isStreaming || data.is_processing || isPolling) && items.length === 0 && !data.progress;

  return (
    <CardContent className="p-0 h-full flex-1 overflow-hidden relative">
      {/* Live Processing Banner */}
      <WebsetsProgressBanner
        isVisible={showProgressBanner}
        message={data.message}
        progress={data.progress}
      />

      {showEmptyState ? (
        <WebsetsEmptyState
          query={data.query}
          isProcessing={true}
        />
      ) : filteredItems.length > 0 ? (
        <ScrollArea className="h-full w-full">
          <div className={cn("p-4", showProgressBanner && "pt-16")}>
            {/* Query Summary */}
            {data.query && (
              <div className="mb-4 p-4 bg-white dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 rounded-lg">
                <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
                  Query: <span className="font-normal text-zinc-600 dark:text-zinc-400">{data.query}</span>
                </div>
                {data.entity_type && (
                  <Badge variant="outline" className="text-xs font-semibold border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300">
                    {data.entity_type}
                  </Badge>
                )}
              </div>
            )}

            {/* Toolbar */}
            <WebsetsToolbar
              searchFilter={searchFilter}
              onSearchChange={onSearchChange}
              items={filteredItems}
              websetId={data.webset_id}
            />

            {/* Data Table */}
            <WebsetsTable
              items={filteredItems}
              allCriteria={allCriteria}
              expandedRows={expandedRows}
              onToggleExpand={onToggleExpand}
            />
          </div>
        </ScrollArea>
      ) : (
        <WebsetsEmptyState
          query={data.query}
          isProcessing={false}
        />
      )}
    </CardContent>
  );
}
