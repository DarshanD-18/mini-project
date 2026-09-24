import React from 'react';
import { useAuth } from '../../../context/AuthContext';
import { Navbar } from '../../../components/layout/Navbar';
import { ModuleCard } from '../components/ModuleCard';
import {
  BookOpen,
  FileQuestion,
  CheckSquare,
  BarChart3,
  Bot,
  Sparkles
} from 'lucide-react';

const modules = [
  {
    title: "Course Progress",
    description: "Track curriculum completion, topic coverage, and daily study milestones.",
    icon: BookOpen,
    color: "bg-blue-50 text-blue-600"
  },
  {
    title: "PYQs (Previous Years)",
    description: "University past question papers categorized by subject, term, and marks weightage.",
    icon: FileQuestion,
    color: "bg-amber-50 text-amber-600"
  },
  {
    title: "Topic-wise Quizzes",
    description: "Practice multiple choice and subjective quizzes with immediate concept explanations.",
    icon: CheckSquare,
    color: "bg-emerald-50 text-emerald-600"
  },
  {
    title: "Performance Analytics",
    description: "Weak area identification, exam readiness score, and predictive grade estimates.",
    icon: BarChart3,
    color: "bg-purple-50 text-purple-600"
  },
  {
    title: "AI Exam Assistant",
    description: "Smart tutor for doubt clearing, syllabus summarization, and customized revision plans.",
    icon: Bot,
    color: "bg-rose-50 text-rose-600"
  }
];

export const DashboardPage = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="bg-gradient-to-r from-indigo-700 via-indigo-600 to-indigo-800 rounded-3xl p-8 sm:p-10 text-white shadow-xl shadow-indigo-100 mb-10 relative overflow-hidden">
          <div className="relative z-10 max-w-2xl">
            <div className="inline-flex items-center gap-2 bg-indigo-500/30 backdrop-blur-md px-3 py-1 rounded-full text-xs font-medium text-indigo-100 mb-4 border border-indigo-400/20">
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>Phase 1 Authentication & Dashboard Shell</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              Welcome back, {user?.name || 'Student'}! 👋
            </h1>
            <p className="mt-2 text-indigo-100 text-sm sm:text-base leading-relaxed">
              Your examination prep hub is ready. Future modules below will be incrementally integrated as you proceed with Phase 2.
            </p>
          </div>
          <div className="absolute right-0 -bottom-10 w-80 h-80 bg-white/5 rounded-full blur-2xl pointer-events-none" />
          <div className="absolute right-40 -top-10 w-60 h-60 bg-indigo-400/10 rounded-full blur-xl pointer-events-none" />
        </div>

        <div>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900 tracking-tight">Academic Modules</h2>
              <p className="text-sm text-slate-500">Upcoming preparation modules planned for implementation</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {modules.map((mod) => (
              <ModuleCard
                key={mod.title}
                title={mod.title}
                description={mod.description}
                icon={mod.icon}
                color={mod.color}
              />
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};
