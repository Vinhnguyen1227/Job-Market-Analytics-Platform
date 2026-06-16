'use client';
import React from 'react';
import Link from 'next/link';

interface Props {
  children: React.ReactNode;
  pageName?: string;
}
interface State { hasError: boolean; error: Error | null; }

export class PageErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error(`[PageErrorBoundary:${this.props.pageName || 'Unknown'}] Uncaught error:`, error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] p-6">
          <div className="bg-white/[0.02] backdrop-blur-md border border-white/10 p-8 rounded-2xl flex flex-col items-center text-center max-w-md w-full shadow-xl">
            <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mb-5 border border-red-500/20">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">
              {this.props.pageName ? `Trang ${this.props.pageName} gặp sự cố` : 'Thành phần này gặp sự cố'}
            </h2>
            <p className="text-slate-400 mb-6 text-sm">
              Không thể tải nội dung trang này do lỗi không mong muốn.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 w-full">
              <button 
                onClick={() => this.setState({ hasError: false, error: null })}
                className="flex-1 px-4 py-2.5 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors"
              >
                Thử lại
              </button>
              <Link 
                href="/"
                className="flex-1 px-4 py-2.5 bg-white/5 hover:bg-white/10 text-white text-sm font-medium rounded-lg border border-white/10 transition-colors text-center"
              >
                Về trang chủ
              </Link>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
