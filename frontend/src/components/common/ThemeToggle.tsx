import React from 'react';
import { Sun, Moon } from 'lucide-react';

interface ThemeToggleProps {
  theme: 'dark' | 'light';
  onToggle: () => void;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ theme, onToggle }) => {
  return (
    <button
      onClick={onToggle}
      className="p-2 rounded-xl bg-dark-900 dark:bg-dark-900 light:bg-slate-100 border border-slate-800 dark:border-slate-800 light:border-slate-300 text-slate-300 dark:text-slate-300 light:text-slate-700 hover:text-white dark:hover:text-white light:hover:text-slate-900 transition-all shadow-sm"
      title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? (
        <Sun className="w-4 h-4 text-amber-400 hover:rotate-45 transition-transform" />
      ) : (
        <Moon className="w-4 h-4 text-indigo-600 hover:-rotate-12 transition-transform" />
      )}
    </button>
  );
};
