import React, { useState, useMemo } from 'react';
import {
  Database,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react';
import { ToolViewProps } from '../types';
import { formatTimestamp, getToolTitle } from '../utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { extractWebsetsData, WebsetData } from './_utils';
import { useWebsetPolling } from './hooks/useWebsetPolling';
import { WebsetsBrowser } from './components/WebsetsBrowser';

export function WebsetsToolView({
  toolCall,
  toolResult,
  assistantTimestamp,
  toolTimestamp,
  isSuccess = true,
  isStreaming = false,
}: ToolViewProps) {
  if (!toolCall) {
    console.warn('WebsetsToolView: toolCall is undefined');
    return null;
  }

  const name = toolCall.function_name.replace(/_/g, '-').toLowerCase();
  const {
    data,
    actualIsSuccess,
    actualToolTimestamp,
    actualAssistantTimestamp
  } = extractWebsetsData(toolCall, toolResult, isSuccess, toolTimestamp, assistantTimestamp);

  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [searchFilter, setSearchFilter] = useState('');

  const toolTitle = getToolTitle(name);

  // Determine view mode based on function name
  const isListItems = name.includes('list-items');
  const isGetWebset = name.includes('get-webset');
  const isListWebsets = name.includes('list-websets');

  // Get webset ID from data - check multiple possible sources
  const websetId = useMemo(() => {
    if (data.webset_id) return data.webset_id;
    
    if (toolResult?.output) {
      const output = toolResult.output as any;
      if (output.webset_id) return output.webset_id;
      if (output.id && typeof output.id === 'string') return output.id;
    }
    
    if (toolCall?.arguments) {
      try {
        const args = typeof toolCall.arguments === 'string' 
          ? JSON.parse(toolCall.arguments) 
          : toolCall.arguments;
        if (args.webset_id) return args.webset_id;
      } catch (e) {
        // Ignore parse errors
      }
    }
    
    return null;
  }, [data.webset_id, toolResult?.output, toolCall?.arguments]);

  // Use polling hook for live updates
  const { liveData, isPolling, effectiveData } = useWebsetPolling({
    websetId,
    initialData: data,
    enabled: !!websetId,
  });

  // Use effective data for items
  const items = useMemo(() => {
    const sourceData = effectiveData;
    if (sourceData.items) return sourceData.items;
    if (sourceData.item) return [sourceData.item];
    return [];
  }, [effectiveData]);

  const toggleExpand = (itemId: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedRows(newExpanded);
  };

  // Handle list-websets view
  if (isListWebsets && data.websets) {
    return (
      <Card className="h-full flex flex-col border-zinc-200 dark:border-zinc-800">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <Database className="h-5 w-5 text-zinc-900 dark:text-zinc-100" />
              {toolTitle}
            </CardTitle>
            {actualIsSuccess !== undefined && (
              <Badge
                variant="secondary"
                className={
                  actualIsSuccess
                    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
                    : "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300"
                }
              >
                {actualIsSuccess ? (
                  <CheckCircle className="h-3.5 w-3.5" />
                ) : (
                  <AlertTriangle className="h-3.5 w-3.5" />
                )}
                {actualIsSuccess ? 'Success' : 'Failed'}
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {data.websets.map((ws: any) => (
              <div key={ws.id} className="p-3 border rounded-lg">
                <div className="font-medium">{ws.name || ws.id}</div>
                <div className="text-sm text-muted-foreground">
                  {ws.item_count || 0} items • {ws.status}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full flex flex-col border-zinc-200 dark:border-zinc-800">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Database className="h-5 w-5 text-zinc-900 dark:text-zinc-100" />
            {toolTitle}
          </CardTitle>
          {actualIsSuccess !== undefined && (
            <Badge
              variant="secondary"
              className={
                actualIsSuccess
                  ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
                  : "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300"
              }
            >
              {actualIsSuccess ? (
                <CheckCircle className="h-3.5 w-3.5" />
              ) : (
                <AlertTriangle className="h-3.5 w-3.5" />
              )}
              {actualIsSuccess ? 'Success' : 'Failed'}
            </Badge>
          )}
        </div>
      </CardHeader>

      <WebsetsBrowser
        data={effectiveData}
        isStreaming={isStreaming}
        isPolling={isPolling}
        items={items}
        onToggleExpand={toggleExpand}
        expandedRows={expandedRows}
        searchFilter={searchFilter}
        onSearchChange={setSearchFilter}
      />

      <div className="px-4 py-2 h-10 bg-zinc-50/90 dark:bg-zinc-900/90 backdrop-blur-sm border-t border-zinc-200 dark:border-zinc-800 flex justify-between items-center gap-4">
        <div className="h-full flex items-center gap-2 text-sm text-zinc-500 dark:text-zinc-400">
          {!isStreaming && items.length > 0 && (
            <Badge variant="outline" className="h-6 py-0.5 text-xs">
              <Database className="h-3 w-3 mr-1" />
              {items.length} results
            </Badge>
          )}
        </div>

        <div className="text-xs text-zinc-500 dark:text-zinc-400">
          {actualToolTimestamp && !isStreaming
            ? formatTimestamp(actualToolTimestamp)
            : actualAssistantTimestamp
              ? formatTimestamp(actualAssistantTimestamp)
              : ''}
        </div>
      </div>
    </Card>
  );
}
