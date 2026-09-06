import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  iconColor?: string;
  iconBg?: string;
  badgeText?: string;
  badgeVariant?: 'success' | 'warning' | 'danger' | 'info';
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  subtext,
  icon: Icon,
  iconColor = 'text-brand-600 dark:text-brand-400',
  iconBg = 'bg-brand-500/10 dark:bg-brand-500/10',
  badgeText,
  badgeVariant = 'info',
}) => {
  const badgeColors = {
    success: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30',
    danger: 'bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/30',
    info: 'bg-brand-500/15 text-brand-600 dark:text-brand-400 border-brand-500/30',
  };

  return (
    <div className="glass-card rounded-xl p-5 relative overflow-hidden transition-all duration-200">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          {label}
        </span>
        <div className={`p-2.5 rounded-lg ${iconBg} ${iconColor}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
          {value}
        </span>
        {badgeText && (
          <span
            className={`text-xs px-2 py-0.5 rounded-full border font-medium ${badgeColors[badgeVariant]}`}
          >
            {badgeText}
          </span>
        )}
      </div>

      {subtext && (
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{subtext}</p>
      )}
    </div>
  );
};
