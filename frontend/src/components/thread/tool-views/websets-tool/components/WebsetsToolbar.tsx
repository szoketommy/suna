import React from 'react';
import { Search, Download } from 'lucide-react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { WebsetItem } from '../types';

interface WebsetsToolbarProps {
  searchFilter: string;
  onSearchChange: (value: string) => void;
  items: WebsetItem[];
  websetId?: string;
}

function convertToCSV(items: WebsetItem[]): string {
  if (items.length === 0) return '';
  
  const headers = ['Name', 'Type', 'Description', 'URL', 'Location', 'Industry', 'Position', 'Company'];
  const rows = items.map(item => [
    item.name || item.title || '',
    item.type || '',
    item.description || '',
    item.url || '',
    item.location || '',
    item.industry || '',
    item.position || '',
    item.company_name || ''
  ]);
  
  return [headers.join(','), ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))].join('\n');
}

function downloadCSV(csv: string, filename: string) {
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

export function WebsetsToolbar({
  searchFilter,
  onSearchChange,
  items,
  websetId,
}: WebsetsToolbarProps) {
  const handleExport = () => {
    const csv = convertToCSV(items);
    downloadCSV(csv, `websets-${websetId || 'export'}.csv`);
  };

  return (
    <div className="flex items-center justify-between mb-4">
      <div className="relative flex-1 max-w-sm">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-zinc-400 dark:text-zinc-500" />
        <Input
          placeholder="Search results..."
          value={searchFilter}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-9 h-9 border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/50 focus:border-zinc-400 dark:focus:border-zinc-600"
        />
      </div>
      <Button 
        variant="outline" 
        size="sm" 
        onClick={handleExport}
        className="border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900/50"
      >
        <Download className="w-4 h-4 mr-2" />
        Export CSV
      </Button>
    </div>
  );
}
