import React from 'react';
import Link from 'next/link';
import { Lock, Sparkles, User, ArrowRight} from 'lucide-react';

interface RequireLoginProps {
  type?: 'ai' | 'profile' | 'default';
}

export default function RequireLogin({ type = 'default' }: RequireLoginProps) {
  const getContext = () => {
    switch (type) {
      case 'ai':
        return {
          title: 'AI Assistant',
          description: 'Chat with our smart AI to analyze the job market, get career advice, and optimize your profile.',
          icon: (
            <div className="relative group/icon">
              <div className="relative w-16 h-16 bg-blue-600 text-white rounded-[24px] flex items-center justify-center shadow-md transform group-hover/icon:scale-105 transition duration-300">
                <Sparkles className="w-8 h-8 text-white" />
                <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-amber-500 border-2 border-white rounded-full flex items-center justify-center text-white shadow-md">
                  <Lock className="w-3.5 h-3.5" />
                </div>
              </div>
            </div>
          ),
        };
      case 'profile':
        return {
          title: 'My Profile',
          description: 'Update your education, work experience, skills, and upload your CV to expand career opportunities and attract employers.',
          icon: (
            <div className="relative group/icon">
              <div className="relative w-16 h-16 bg-blue-600 text-white rounded-[24px] flex items-center justify-center shadow-md transform group-hover/icon:scale-105 transition duration-300">
                <User className="w-8 h-8 text-white" />
                <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-amber-500 border-2 border-white rounded-full flex items-center justify-center text-white shadow-md">
                  <Lock className="w-3.5 h-3.5" />
                </div>
              </div>
            </div>
          ),
        };
      default:
        return {
          title: 'Feature Requires Login',
          description: 'Please log in to your account to access and use all the smart career analysis tools.',
          icon: (
            <div className="relative group/icon">
              <div className="absolute -inset-2 bg-gradient-to-r from-amber-500 to-red-500 rounded-2xl blur-xl opacity-40 group-hover/icon:opacity-60 transition duration-500 animate-pulse"></div>
              <div className="relative w-16 h-16 bg-gradient-to-tr from-amber-500 to-red-600 text-white rounded-2xl flex items-center justify-center shadow-lg shadow-amber-500/20 transform group-hover/icon:scale-110 transition duration-300">
                <Lock className="w-8 h-8" />
              </div>
            </div>
          ),
        };
    }
  };

  const context = getContext();

  return (
    <div className="flex-1 flex items-center justify-center p-6 bg-[#f4f2ee] min-h-[75vh] animate-in fade-in slide-in-from-bottom-8 duration-500">
      <div className="group relative bg-white p-8 md:p-12 rounded-3xl shadow-[0_15px_50px_-15px_rgba(0,0,0,0.06)] border border-gray-100 w-full max-w-lg text-center transition-all duration-300 hover:shadow-[0_20px_60px_-10px_rgba(0,0,0,0.1)]">
        
        {/* Glow effect at corners */}
        <div className="absolute top-0 left-0 w-32 h-32 bg-blue-50 rounded-full filter blur-3xl opacity-50 pointer-events-none -translate-x-1/2 -translate-y-1/2 transition-all group-hover:scale-125"></div>
        <div className="absolute bottom-0 right-0 w-32 h-32 bg-indigo-50 rounded-full filter blur-3xl opacity-50 pointer-events-none translate-x-1/2 translate-y-1/2 transition-all group-hover:scale-125"></div>

        {/* Icon */}
        <div className="flex justify-center mb-8">
          {context.icon}
        </div>

        {/* Title */}
        <h2 className="text-2xl md:text-3xl font-extrabold text-slate-800 tracking-tight leading-tight mb-3">
          {context.title}
        </h2>
        
        {/* Exact text request with beautiful highlighting */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-50 border border-amber-100 text-amber-800 text-xs font-semibold uppercase tracking-wider mb-6 shadow-sm">
          <span>please log in to use this feature</span>
        </div>

        {/* Description */}
        <p className="text-gray-500 text-sm md:text-base mb-8 leading-relaxed max-w-md mx-auto font-light">
          {context.description}
        </p>

        {/* Interactive Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link href="/signup" className="w-full sm:w-auto">
            <button className="w-full sm:w-auto bg-[#f27a42] hover:bg-[#e06830] text-white font-bold px-8 py-3.5 rounded-xl shadow-md hover:-translate-y-0.5 transition duration-200 flex items-center justify-center cursor-pointer">
              Sign up
            </button>
          </Link>

          <Link href="/login" className="w-full sm:w-auto">
            <button className="w-full sm:w-auto bg-gray-100 hover:bg-gray-200 text-slate-800 font-semibold px-8 py-3.5 rounded-xl shadow-sm hover:-translate-y-0.5 transition duration-200 flex items-center justify-center gap-2 cursor-pointer border border-transparent">
              Log In
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}
