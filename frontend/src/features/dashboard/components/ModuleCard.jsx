import React from 'react';
import { ArrowUpRight } from 'lucide-react';

export const ModuleCard = ({ title, description, icon: Icon, color, status = "Upcoming in Phase 2" }) => {
  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-all duration-200 flex flex-col justify-between group">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 rounded-xl ${color}`}>
            <Icon className="w-6 h-6" />
          </div>
          <span className="text-[11px] font-semibold tracking-wide uppercase px-2.5 py-1 bg-slate-100 text-slate-600 rounded-full">
            {status}
          </span>
        </div>
        <h3 className="text-lg font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">
          {title}
        </h3>
        <p className="text-sm text-slate-500 mt-2 leading-relaxed">
          {description}
        </p>
      </div>

      <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
        <span>Module placeholder</span>
        <ArrowUpRight className="w-4 h-4 opacity-50 group-hover:opacity-100 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
      </div>
    </div>
  );
};
