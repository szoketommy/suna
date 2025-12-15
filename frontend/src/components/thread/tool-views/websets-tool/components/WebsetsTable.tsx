import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ChevronDown } from "lucide-react";
import { cn } from '@/lib/utils';
import { WebsetItem } from '../types';
import { getEntityIcon } from '../utils/entity-icons';

// Fix type issue - ensure type is always defined
function ensureType(item: WebsetItem): string {
  return item.type || 'unknown';
}

interface WebsetsTableProps {
  items: WebsetItem[];
  allCriteria: string[];
  expandedRows: Set<string>;
  onToggleExpand: (itemId: string) => void;
}

export function WebsetsTable({
  items,
  allCriteria,
  expandedRows,
  onToggleExpand,
}: WebsetsTableProps) {
  if (items.length === 0) {
    return null;
  }

  const entityType = ensureType(items[0])?.toLowerCase() || '';
  const isPerson = entityType === 'person';

  const getEvaluationForCriterion = (item: WebsetItem, criterion: string) => {
    return item.evaluations?.find(e => e.criterion === criterion);
  };

  const getReferenceCount = (evaluation: any) => {
    if (evaluation?.reasoning) {
      const refMatches = evaluation.reasoning.match(/\d+\s*ref/i);
      return refMatches ? parseInt(refMatches[0]) : 1;
    }
    return 1;
  };

  return (
    <div className="w-full overflow-x-auto">
      <Table className="border-separate border-spacing-0 min-w-full">
        <TableHeader className="bg-zinc-50 dark:bg-zinc-900/50 sticky top-0 z-10 border-b border-zinc-200 dark:border-zinc-800">
          <TableRow>
            <TableHead className="w-12"></TableHead>
            <TableHead className="min-w-[200px] font-semibold text-zinc-900 dark:text-zinc-100">Name</TableHead>
            {isPerson && (
              <TableHead className="min-w-[150px] font-semibold text-zinc-900 dark:text-zinc-100">Role</TableHead>
            )}
            <TableHead className="min-w-[200px] font-semibold text-zinc-900 dark:text-zinc-100">URL</TableHead>
            {allCriteria.map((criterion, idx) => (
              <TableHead key={idx} className="min-w-[140px] text-center font-semibold text-zinc-900 dark:text-zinc-100">
                <div className="flex flex-col items-center gap-1">
                  <span className="text-xs font-semibold truncate max-w-[120px]" title={criterion}>
                    {criterion}
                  </span>
                </div>
              </TableHead>
            ))}
            <TableHead className="w-12"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((item) => {
            const EntityIcon = getEntityIcon(ensureType(item));
            const isExpanded = expandedRows.has(item.id);

            return (
              <React.Fragment key={item.id}>
                <TableRow 
                  className={cn(
                    "group hover:bg-zinc-50 dark:hover:bg-zinc-900/30 cursor-pointer border-b border-zinc-200 dark:border-zinc-800 transition-colors",
                    isExpanded && "bg-zinc-50 dark:bg-zinc-900/20"
                  )}
                  onClick={() => onToggleExpand(item.id)}
                >
                  <TableCell className="w-12">
                    {isPerson && item.picture_url ? (
                      <Avatar className="w-9 h-9 border border-zinc-200 dark:border-zinc-700">
                        <AvatarImage src={item.picture_url} alt={item.name} />
                        <AvatarFallback className="bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">
                          <EntityIcon className="w-4 h-4" />
                        </AvatarFallback>
                      </Avatar>
                    ) : !isPerson && item.logo_url ? (
                      <Avatar className="w-9 h-9 border border-zinc-200 dark:border-zinc-700">
                        <AvatarImage src={item.logo_url} alt={item.name} />
                        <AvatarFallback className="bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">
                          <EntityIcon className="w-4 h-4" />
                        </AvatarFallback>
                      </Avatar>
                    ) : (
                      <div className="w-9 h-9 rounded-full bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 flex items-center justify-center">
                        <EntityIcon className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
                      </div>
                    )}
                  </TableCell>
                  <TableCell className="font-semibold min-w-[200px] text-zinc-900 dark:text-zinc-100">
                    <div className="flex items-center gap-2">
                      {item.name || item.title || 'Unknown'}
                    </div>
                  </TableCell>
                  {isPerson && (
                    <TableCell className="text-zinc-600 dark:text-zinc-400 min-w-[150px]">
                      {item.position || '-'}
                    </TableCell>
                  )}
                  <TableCell className="min-w-[200px]">
                    {item.url ? (
                      <a 
                        href={item.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:underline text-sm truncate block font-mono"
                      >
                        {item.url.replace(/^https?:\/\//, '').substring(0, 40)}...
                      </a>
                    ) : (
                      <span className="text-zinc-400 dark:text-zinc-500">-</span>
                    )}
                  </TableCell>
                  {allCriteria.map((criterion, critIdx) => {
                    const evaluation = getEvaluationForCriterion(item, criterion);
                    const refCount = evaluation ? getReferenceCount(evaluation) : 0;
                    const satisfied = evaluation?.satisfied || 'unclear';
                    
                    return (
                      <TableCell key={critIdx} className="text-center min-w-[140px]">
                        {evaluation ? (
                          <div className="flex flex-col items-center gap-1">
                            <Badge 
                              variant="outline"
                              className={cn(
                                "text-xs font-semibold border-2",
                                satisfied === 'yes' && "bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300",
                                satisfied === 'no' && "bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300",
                                satisfied === 'unclear' && "bg-zinc-100 dark:bg-zinc-800 border-zinc-300 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400"
                              )}
                            >
                              {satisfied === 'yes' ? 'Match' : satisfied === 'no' ? 'Miss' : 'Unclear'}
                            </Badge>
                            {refCount > 0 && (
                              <span className="text-xs text-zinc-500 dark:text-zinc-400 font-medium">
                                {refCount} ref{refCount !== 1 ? 's' : ''}
                              </span>
                            )}
                          </div>
                        ) : (
                          <span className="text-zinc-400 dark:text-zinc-500 text-xs">-</span>
                        )}
                      </TableCell>
                    );
                  })}
                  <TableCell className="w-12">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-8 w-8 p-0 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                      onClick={(e) => {
                        e.stopPropagation();
                        onToggleExpand(item.id);
                      }}
                    >
                      <ChevronDown className={cn("w-4 h-4 text-zinc-600 dark:text-zinc-400 transition-transform", isExpanded && "rotate-180")} />
                    </Button>
                  </TableCell>
                </TableRow>
                {isExpanded && (
                  <TableRow>
                    <TableCell colSpan={3 + allCriteria.length + 1} className="bg-zinc-50 dark:bg-zinc-900/40 p-6 border-b border-zinc-200 dark:border-zinc-800">
                      <div className="space-y-6">
                        {item.description && (
                          <div>
                            <div className="text-xs font-bold uppercase tracking-wide text-zinc-500 dark:text-zinc-400 mb-2">Description</div>
                            <div className="text-sm text-zinc-900 dark:text-zinc-100 leading-relaxed">{item.description}</div>
                          </div>
                        )}
                        {item.evaluations && item.evaluations.length > 0 && (
                          <div>
                            <div className="text-xs font-bold uppercase tracking-wide text-zinc-500 dark:text-zinc-400 mb-3">Criteria Evaluation</div>
                            <div className="space-y-3">
                              {item.evaluations.map((evaluation, idx) => (
                                <div key={idx} className="flex items-start gap-3 p-3 bg-white dark:bg-zinc-900/50 rounded-lg border border-zinc-200 dark:border-zinc-800">
                                  <div className={cn(
                                    "w-2.5 h-2.5 rounded-full shrink-0 mt-1.5",
                                    evaluation.satisfied === 'yes' ? "bg-emerald-500" : 
                                    evaluation.satisfied === 'no' ? "bg-red-500" : "bg-zinc-400"
                                  )} />
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                      <span className="font-semibold text-zinc-900 dark:text-zinc-100 text-sm">{evaluation.criterion}</span>
                                      <Badge 
                                        variant="outline"
                                        className={cn(
                                          "text-xs font-semibold border",
                                          evaluation.satisfied === 'yes' && "bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300",
                                          evaluation.satisfied === 'no' && "bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300",
                                          evaluation.satisfied === 'unclear' && "bg-zinc-100 dark:bg-zinc-800 border-zinc-300 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400"
                                        )}
                                      >
                                        {evaluation.satisfied}
                                      </Badge>
                                    </div>
                                    {evaluation.reasoning && (
                                      <div className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed mt-1">
                                        {evaluation.reasoning}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        {item.enrichments && Object.keys(item.enrichments).length > 0 && (
                          <div>
                            <div className="text-xs font-bold uppercase tracking-wide text-zinc-500 dark:text-zinc-400 mb-3">Enrichments</div>
                            <div className="flex flex-wrap gap-2">
                              {Object.entries(item.enrichments).map(([key, value]) => (
                                <div key={key} className="px-3 py-1.5 bg-white dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 rounded-md">
                                  <span className="text-xs font-semibold text-zinc-900 dark:text-zinc-100">{key}:</span>
                                  <span className="text-xs text-zinc-600 dark:text-zinc-400 ml-1">{String(value)}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </React.Fragment>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
