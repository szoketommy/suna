import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { backendApi } from '@/lib/api-client';
import { WebsetData, WebsetItem } from '../types';

interface UseWebsetPollingOptions {
  websetId: string | null;
  initialData: WebsetData;
  enabled?: boolean;
}

interface UseWebsetPollingReturn {
  liveData: WebsetData | null;
  isPolling: boolean;
  pollWebsetStatus: () => Promise<void>;
  effectiveData: WebsetData;
}

export function useWebsetPolling({
  websetId,
  initialData,
  enabled = true,
}: UseWebsetPollingOptions): UseWebsetPollingReturn {
  const [liveData, setLiveData] = useState<WebsetData | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const pollCountRef = useRef(0);

  // Merge live data with initial data
  const effectiveData = liveData || initialData;

  // Determine if we should poll
  const shouldPoll = useMemo(() => {
    if (!websetId || !enabled) return false;
    
    // If we have explicit processing flags, use them
    if (initialData.is_processing !== undefined || effectiveData.is_processing !== undefined) {
      return (initialData.is_processing || effectiveData.is_processing) && !effectiveData.is_complete;
    }
    
    // If status indicates processing, poll
    const status = effectiveData.status || initialData.status;
    if (status && ['running', 'pending'].includes(status)) {
      return true;
    }
    
    // If we have a webset_id but no status yet, poll once to get status
    if (websetId && !status && !effectiveData.is_complete) {
      return true;
    }
    
    return false;
  }, [websetId, enabled, initialData.is_processing, initialData.status, effectiveData.is_processing, effectiveData.status, effectiveData.is_complete]);

  // Poll for live updates
  const pollWebsetStatus = useCallback(async () => {
    if (!websetId) {
      console.warn('[useWebsetPolling] No webset_id available for polling');
      return;
    }
    
    try {
      const response = await backendApi.get<{
        webset_id: string;
        status: string;
        search_status?: string;
        is_processing: boolean;
        is_complete: boolean;
        progress?: {
          found: number;
          analyzed: number;
          completion: number;
          time_left?: number | null;
        };
        items_found: number;
        items_returned: number;
        items?: WebsetItem[];
        message: string;
      }>(`/websets/${websetId}/status?include_items=true&item_limit=100`);
      
      if (response.success && response.data) {
        const apiData = response.data;
        
        // Merge items intelligently - avoid duplicates by ID
        const existingItemIds = new Set(
          (liveData?.items || initialData.items || []).map(item => item.id)
        );
        
        const newItems = (apiData.items || []).filter(
          item => item.id && !existingItemIds.has(item.id)
        );
        
        const mergedItems = [
          ...(liveData?.items || initialData.items || []),
          ...newItems
        ];
        
        // Update live data with fresh API response
        setLiveData({
          webset_id: apiData.webset_id,
          status: apiData.status,
          search_status: apiData.search_status,
          is_processing: apiData.is_processing,
          is_complete: apiData.is_complete,
          progress: apiData.progress,
          items_found: apiData.items_found,
          items_returned: apiData.items_returned,
          message: apiData.message,
          // Preserve original data fields
          query: initialData.query || effectiveData.query,
          entity_type: initialData.entity_type || effectiveData.entity_type,
          external_id: initialData.external_id || effectiveData.external_id,
          cost_deducted: initialData.cost_deducted || effectiveData.cost_deducted,
          // Use merged items
          items: mergedItems,
        });
        
        // Stop polling if complete
        if (apiData.is_complete) {
          setIsPolling(false);
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
          console.log(`[useWebsetPolling] Webset ${websetId} completed with ${apiData.items_found} items`);
        }
        
        // Reset error count on successful poll
        pollCountRef.current = 0;
      } else {
        console.warn('[useWebsetPolling] Poll response not successful:', response);
      }
    } catch (error: any) {
      console.error('[useWebsetPolling] Polling error:', error);
      
      // Increment error count
      pollCountRef.current++;
      
      // Stop polling after too many consecutive errors
      if (pollCountRef.current >= 10) {
        console.error(`[useWebsetPolling] Stopping polling after ${pollCountRef.current} consecutive errors`);
        setIsPolling(false);
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      }
    }
  }, [websetId, initialData, liveData, effectiveData]);

  // Fetch initial data if we have a webset_id but no items
  useEffect(() => {
    if (websetId && !liveData && (initialData.items?.length === 0 || !initialData.items) && !isPolling && enabled) {
      console.log(`[useWebsetPolling] Fetching initial data for webset ${websetId}`);
      pollWebsetStatus();
    }
  }, [websetId, liveData, initialData.items, isPolling, enabled, pollWebsetStatus]);

  // Start polling when webset is processing
  useEffect(() => {
    if (!websetId || !enabled) {
      return;
    }
    
    if (shouldPoll && !isPolling && !pollingIntervalRef.current) {
      console.log(`[useWebsetPolling] Starting polling for webset ${websetId}`);
      setIsPolling(true);
      pollCountRef.current = 0;
      
      // Initial poll immediately
      pollWebsetStatus();
      
      // Poll every 2 seconds while processing
      pollingIntervalRef.current = setInterval(() => {
        pollWebsetStatus();
      }, 2000);
    } else if (!shouldPoll && pollingIntervalRef.current) {
      // Stop polling if webset is complete
      console.log(`[useWebsetPolling] Stopping polling for webset ${websetId} - processing complete`);
      setIsPolling(false);
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }
    
    // Cleanup on unmount or when websetId changes
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [shouldPoll, isPolling, pollWebsetStatus, websetId, enabled]);

  return {
    liveData,
    isPolling,
    pollWebsetStatus,
    effectiveData,
  };
}
