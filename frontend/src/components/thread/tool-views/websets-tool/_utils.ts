import { ToolCallData, ToolResultData } from '../types';
import type { WebsetItem, WebsetData } from './types';

// Re-export types from centralized location
export type { WebsetItem, WebsetData } from './types';

export function extractWebsetsData(
  toolCall: ToolCallData,
  toolResult: ToolResultData | undefined,
  isSuccess: boolean,
  toolTimestamp?: string,
  assistantTimestamp?: string
): {
  data: WebsetData;
  actualIsSuccess: boolean;
  actualToolTimestamp?: string;
  actualAssistantTimestamp?: string;
} {
  const args = toolCall.arguments || {};
  
  let data: WebsetData = {
    webset_id: args.webset_id || null,
    query: args.query || null,
    entity_type: args.entity_type || null,
  };

  // Extract from toolResult output
  if (toolResult?.output) {
    const output = toolResult.output;
    let parsedOutput: any = {};
    
    if (typeof output === 'string') {
      try {
        parsedOutput = JSON.parse(output);
      } catch (e) {
        // Not JSON, keep empty
      }
    } else if (typeof output === 'object' && output !== null) {
      parsedOutput = output;
    }

    // Handle different response structures based on method
    if (parsedOutput.websets) {
      // list_websets response
      data = {
        websets: parsedOutput.websets,
        total: parsedOutput.total || 0
      };
    } else if (parsedOutput.items) {
      // list_items response
      data = {
        webset_id: parsedOutput.webset_id,
        items: parsedOutput.items || [],
        total: parsedOutput.total || 0,
        limit: parsedOutput.limit,
        next_cursor: parsedOutput.next_cursor,
        has_more: parsedOutput.has_more
      };
    } else if (parsedOutput.item) {
      // get_item response
      data = {
        webset_id: parsedOutput.webset_id,
        item: parsedOutput.item
      };
    } else if (parsedOutput.searches) {
      // list_searches response
      data = {
        webset_id: parsedOutput.webset_id,
        searches: parsedOutput.searches,
        total: parsedOutput.total || 0
      };
    } else if (parsedOutput.monitors) {
      // list_monitors response
      data = {
        monitors: parsedOutput.monitors,
        total: parsedOutput.total || 0
      };
    } else {
      // create_webset, get_webset, poll_webset_status, or other responses
      data = {
        webset_id: parsedOutput.webset_id || parsedOutput.id,
        external_id: parsedOutput.external_id,
        query: parsedOutput.query || args.query,
        entity_type: parsedOutput.entity_type || args.entity_type,
        status: parsedOutput.status,
        search_status: parsedOutput.search_status,
        item_count: parsedOutput.item_count || parsedOutput.items_found,
        items_found: parsedOutput.items_found,
        items_returned: parsedOutput.items_returned,
        cost_deducted: parsedOutput.cost_deducted,
        items: parsedOutput.items,
        // Live processing fields
        is_processing: parsedOutput.is_processing,
        is_complete: parsedOutput.is_complete,
        progress: parsedOutput.progress,
        message: parsedOutput.message,
        searches: parsedOutput.searches,
        enrichments: parsedOutput.enrichments,
        monitors: parsedOutput.monitors,
        created_at: parsedOutput.created_at,
        updated_at: parsedOutput.updated_at
      };
    }
  }

  const actualIsSuccess = toolResult?.success !== undefined ? toolResult.success : isSuccess;

  return {
    data,
    actualIsSuccess,
    actualToolTimestamp: toolTimestamp,
    actualAssistantTimestamp: assistantTimestamp
  };
}
