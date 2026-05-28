import React from 'react';
import Link from 'next/link';
import { BarChart2 } from 'lucide-react';
import { logout } from '@/backend/auth/actions';

interface NavbarProps {
  user?: any;
  activeTab?: 'home' | 'search' | 'insights' | 'ai' | 'profile' | 'none';
}

export default function Navbar({ user, activeTab = 'none' }: NavbarProps) {
  const getTabClass = (tab: 'home' | 'search' | 'insights' | 'ai' | 'profile') => {
    if (activeTab === tab) {
      return "text-blue-600 border-b-2 border-blue-600 pb-1";
    }
    return "hover:text-blue-600 transition";
  };

  return (
    <nav className="flex justify-between items-center px-6 md:px-12 py-4 bg-white z-20 relative shadow-sm shrink-0">
      <Link href="/" className="flex items-center gap-3">
        <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center text-white animate-in fade-in zoom-in duration-300">
          <BarChart2 size={24} className="text-blue-400" />
        </div>
        <span className="font-bold text-2xl text-slate-800 select-none">
          Career<span className="text-blue-600">Intel</span>
          <span className="block text-[10px] text-gray-500 font-normal -mt-1">Intelligent Job Market Hub</span>
        </span>
      </Link>

      <div className="hidden lg:flex items-center gap-8 font-semibold text-sm text-slate-800">
        <Link href="/search" className={getTabClass('search')}>
          Job Search
        </Link>
        <Link href="/insights" className={getTabClass('insights')}>
          Market Insights
        </Link>
        <Link href="/ai" className={getTabClass('ai')}>
          AI Assistant
        </Link>
        <Link href="/profile" className={getTabClass('profile')}>
          My Profile
        </Link>
      </div>

      <div className="hidden lg:flex items-center gap-4 font-semibold text-sm text-slate-800">
        {user ? (
          <>
            <div className="flex items-center gap-2 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                {user.user_metadata?.full_name?.charAt(0)?.toUpperCase() || user.email?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <span>Hi, {user.user_metadata?.full_name || 'User'}</span>
            </div>
            <button
              onClick={() => logout()}
              className="bg-gray-100 hover:bg-gray-200 text-slate-800 px-6 py-2.5 rounded-md font-medium transition shadow-sm cursor-pointer"
            >
              Log Out
            </button>
          </>
        ) : (
          <>
            <Link href="/signup">
              <button className="bg-[#f27a42] hover:bg-[#e06830] text-white px-6 py-2.5 rounded-md font-medium transition shadow-md cursor-pointer">
                Sign Up
              </button>
            </Link>
            <Link href="/login">
              <button className="bg-gray-100 hover:bg-gray-200 text-slate-800 px-6 py-2.5 rounded-md font-medium transition shadow-sm cursor-pointer">
                Log In
              </button>
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
