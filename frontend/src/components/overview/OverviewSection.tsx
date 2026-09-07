import React from 'react';
import { FullEDAReport, ColumnProfile } from '../../types/eda';
import { QualityGauge } from '../common/QualityGauge';
import { StatCard } from '../common/StatCard';
import { SchemaTable } from './SchemaTable';
import {
  Database,
  Columns3,
  AlertCircle,
  Copy,
  Cpu,
  Fingerprint,
} from 'lucide-react';

interface OverviewSectionProps {
  report: FullEDAReport;
  onColumnClick?: (column: ColumnProfile) => void;
}

export const OverviewSection: React.FC<OverviewSectionProps> = ({ report, onColumnClick }) => {
  const { profiler, missing, duplicates, outliers, insights } = report;

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* 1. Quality Score Hero */}
      <QualityGauge score={insights.quality_score} />

      {/* 2. Key Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <StatCard
          label="Total Records"
          value={profiler.rows_count.toLocaleString()}
          subtext="Dataset observations"
          icon={Database}
          iconColor="text-brand-400"
          iconBg="bg-brand-500/10"
        />

        <StatCard
          label="Features"
          value={profiler.columns_count}
          subtext={`${profiler.numeric_columns.length} num • ${profiler.categorical_columns.length} cat`}
          icon={Columns3}
          iconColor="text-indigo-400"
          iconBg="bg-indigo-500/10"
        />

        <StatCard
          label="Missing Cells"
          value={`${missing.overall_missing_percentage}%`}
          subtext={`${missing.total_missing_cells.toLocaleString()} empty values`}
          icon={AlertCircle}
          iconColor={missing.overall_missing_percentage > 5 ? 'text-rose-400' : 'text-emerald-400'}
          iconBg={missing.overall_missing_percentage > 5 ? 'bg-rose-500/10' : 'bg-emerald-500/10'}
          badgeText={missing.has_systematic_missingness ? 'Systematic' : undefined}
          badgeVariant="warning"
        />

        <StatCard
          label="Duplicate Rows"
          value={`${duplicates.duplicate_percentage}%`}
          subtext={`${duplicates.duplicate_rows_count.toLocaleString()} duplicate records`}
          icon={Copy}
          iconColor={duplicates.has_duplicates ? 'text-amber-400' : 'text-slate-400'}
          iconBg={duplicates.has_duplicates ? 'bg-amber-500/10' : 'bg-slate-800'}
        />

        <StatCard
          label="Outlier Flags"
          value={`${outliers.multivariate_anomaly_percentage}%`}
          subtext={`${outliers.total_flagged_rows.toLocaleString()} anomalies`}
          icon={Fingerprint}
          iconColor="text-purple-400"
          iconBg="bg-purple-500/10"
        />

        <StatCard
          label="Memory Usage"
          value={profiler.total_memory_formatted}
          subtext="In-memory footprint"
          icon={Cpu}
          iconColor="text-cyan-400"
          iconBg="bg-cyan-500/10"
        />
      </div>

      {/* 3. Schema & Feature Typing Table */}
      <SchemaTable columns={profiler.columns} onColumnClick={onColumnClick} />
    </div>
  );
};
