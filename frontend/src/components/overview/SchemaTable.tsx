import React, { useState } from 'react';
import { ColumnProfile } from '../../types/eda';
import { Search, Hash, Type, Calendar, ToggleLeft, Key, Lock } from 'lucide-react';
import { Badge } from '../common/Badge';

interface SchemaTableProps {
  columns: ColumnProfile[];
}

export const SchemaTable: React.FC<SchemaTableProps> = ({ columns }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  const filteredColumns = columns.filter((col) => {
    const matchesSearch = col.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = typeFilter === 'all' || col.inferred_type === typeFilter;
    return matchesSearch && matchesType;
  });

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'numeric':
        return <Hash className="w-3.5 h-3.5 text-blue-500 dark:text-blue-400" />;
      case 'categorical':
        return <Type className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" />;
      case 'boolean':
        return <ToggleLeft className="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400" />;
      case 'datetime':
        return <Calendar className="w-3.5 h-3.5 text-purple-500 dark:text-purple-400" />;
      case 'id_like':
        return <Key className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400" />;
      case 'constant':
        return <Lock className="w-3.5 h-3.5 text-rose-500 dark:text-rose-400" />;
      default:
        return <Type className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />;
    }
  };

  const getTypeBadgeVariant = (type: string) => {
    switch (type) {
      case 'numeric':
        return 'primary';
      case 'categorical':
        return 'success';
      case 'boolean':
        return 'info';
      case 'datetime':
        return 'info';
      case 'id_like':
        return 'warning';
      case 'constant':
        return 'danger';
      default:
        return 'neutral';
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 transition-colors">
      {/* Header with Search and Type Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
            Dataset Schema & Semantic Type Inference
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Auto-classified {columns.length} columns based on cardinality, dtypes, and value patterns.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          {/* Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search column..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-white dark:bg-dark-900 border border-slate-200 dark:border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-900 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:border-brand-500 transition-colors w-44"
            />
          </div>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-white dark:bg-dark-900 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-900 dark:text-slate-200 focus:outline-none focus:border-brand-500 transition-colors"
          >
            <option value="all">All Types</option>
            <option value="numeric">Numeric</option>
            <option value="categorical">Categorical</option>
            <option value="boolean">Boolean</option>
            <option value="datetime">Datetime</option>
            <option value="id_like">ID / Key</option>
            <option value="constant">Constant</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 uppercase tracking-wider font-semibold">
              <th className="pb-3 px-3">Column Name</th>
              <th className="pb-3 px-3">Pandas Dtype</th>
              <th className="pb-3 px-3">Inferred Semantic Type</th>
              <th className="pb-3 px-3 text-right">Unique Values</th>
              <th className="pb-3 px-3 text-right">Missing Count (%)</th>
              <th className="pb-3 px-3">Sample Values</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-sans">
            {filteredColumns.map((col) => (
              <tr key={col.name} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                <td className="py-3 px-3 font-semibold text-slate-900 dark:text-white">
                  {col.name}
                </td>
                <td className="py-3 px-3 font-mono text-slate-500 dark:text-slate-400">
                  {col.dtype}
                </td>
                <td className="py-3 px-3">
                  <div className="flex items-center gap-1.5">
                    {getTypeIcon(col.inferred_type)}
                    <Badge variant={getTypeBadgeVariant(col.inferred_type)}>
                      {col.inferred_type}
                    </Badge>
                  </div>
                </td>
                <td className="py-3 px-3 text-right font-mono text-slate-700 dark:text-slate-300">
                  {col.unique_count.toLocaleString()}{' '}
                  <span className="text-[10px] text-slate-400 dark:text-slate-500">
                    ({(col.unique_ratio * 100).toFixed(1)}%)
                  </span>
                </td>
                <td className="py-3 px-3 text-right">
                  {col.null_count > 0 ? (
                    <span className="font-mono text-rose-500 dark:text-rose-400 font-medium">
                      {col.null_count.toLocaleString()}{' '}
                      <span className="text-[10px]">
                        ({(col.null_ratio * 100).toFixed(1)}%)
                      </span>
                    </span>
                  ) : (
                    <span className="font-mono text-slate-400 dark:text-slate-500">0 (0.0%)</span>
                  )}
                </td>
                <td className="py-3 px-3">
                  <div className="flex items-center gap-1 overflow-hidden max-w-xs">
                    {col.sample_values.slice(0, 3).map((val, idx) => (
                      <span
                        key={idx}
                        className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-dark-900 border border-slate-200 dark:border-slate-800 text-[10px] font-mono text-slate-600 dark:text-slate-400 truncate"
                      >
                        {String(val)}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
