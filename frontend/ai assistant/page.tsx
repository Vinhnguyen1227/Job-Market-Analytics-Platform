"use client";

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import {
  BarChart2,
  Plus,
  Search,
  MessageSquare,
  Send,
  Sparkles,
  Trash2,
  Paperclip,
  FileText,
  Loader2,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { logout } from '@/backend/auth/actions';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  taskType?: string;
  metadata?: Record<string, unknown>;
}

interface Chat {
  id: string;
  title: string;
  messages: Message[];
  sessionId?: string;
  resumeId?: string;
  resumeName?: string;
}

const SAMPLE_CHATS: Chat[] = [
  { id: '1', title: 'Phân tích xu hướng tuyển dụng IT', messages: [] },
  { id: '2', title: 'Tư vấn lộ trình nghề nghiệp', messages: [] },
  { id: '3', title: 'So sánh mức lương ngành Data', messages: [] },
  { id: '4', title: 'Kỹ năng cần thiết cho Product Manager', messages: [] },
  { id: '5', title: 'Top công ty công nghệ tại Hà Nội', messages: [] },
];

export default function AIAssistantPage({ user }: { user?: any }) {
  const [chats, setChats] = useState<Chat[]>(SAMPLE_CHATS);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [resumeId, setResumeId] = useState<string | null>(null);
  const [resumeName, setResumeName] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const activeChat = chats.find(c => c.id === activeChatId);

  const filteredChats = chats.filter(c =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleNewChat = () => {
    setActiveChatId(null);
    setMessages([]);
    setInputValue('');
    setSessionId(null);
    setResumeId(null);
    setResumeName(null);
  };

  const handleSelectChat = (chatId: string) => {
    setActiveChatId(chatId);
    const chat = chats.find(c => c.id === chatId);
    setMessages(chat?.messages || []);
    setSessionId(chat?.sessionId || null);
    setResumeId(chat?.resumeId || null);
    setResumeName(chat?.resumeName || null);
  };

  const handleDeleteChat = (e: React.MouseEvent, chatId: string) => {
    e.stopPropagation();
    setChats(prev => prev.filter(c => c.id !== chatId));
    if (activeChatId === chatId) {
      setActiveChatId(null);
      setMessages([]);
      setSessionId(null);
      setResumeId(null);
      setResumeName(null);
    }
  };

  const handleSend = async () => {
    const text = inputValue.trim();
    if (!text || isTyping) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: text };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInputValue('');
    setIsTyping(true);

    // Create or update chat
    let currentChatId = activeChatId;
    if (!currentChatId) {
      const newChat: Chat = {
        id: Date.now().toString(),
        title: text.length > 40 ? text.slice(0, 40) + '...' : text,
        messages: [],
        sessionId: sessionId || undefined,
        resumeId: resumeId || undefined,
        resumeName: resumeName || undefined,
      };
      setChats(prev => [newChat, ...prev]);
      setActiveChatId(newChat.id);
      currentChatId = newChat.id;
    }

    try {
      // Call the chatbot API
      const response = await fetch('/api/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
          history: newMessages.slice(-10).map(m => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      const data = await response.json();

      // Update session ID from backend
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
        setChats(prev => prev.map(c =>
          c.id === currentChatId ? { ...c, sessionId: data.session_id } : c
        ));
      }

      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'Xin lỗi, tôi không thể trả lời lúc này.',
        taskType: data.task_type,
        metadata: data.metadata,
      };

      const updatedMessages = [...newMessages, aiMsg];
      setMessages(updatedMessages);
      setChats(prev => prev.map(c =>
        c.id === currentChatId ? { ...c, messages: updatedMessages } : c
      ));
    } catch (error) {
      console.error('Chat error:', error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '❌ Không thể kết nối đến server. Vui lòng kiểm tra lại kết nối.',
      };

      const updatedMessages = [...newMessages, errorMsg];
      setMessages(updatedMessages);
      setChats(prev => prev.map(c =>
        c.id === currentChatId ? { ...c, messages: updatedMessages } : c
      ));
    } finally {
      setIsTyping(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reset file input
    if (fileInputRef.current) fileInputRef.current.value = '';

    setIsUploading(true);

    // Show upload-in-progress message
    const uploadMsg: Message = {
      id: Date.now().toString(),
      role: 'system',
      content: `📤 Đang tải lên và xử lý **${file.name}**...`,
    };

    // Create chat if needed
    let currentChatId = activeChatId;
    if (!currentChatId) {
      const newChat: Chat = {
        id: Date.now().toString(),
        title: `📄 ${file.name}`,
        messages: [],
      };
      setChats(prev => [newChat, ...prev]);
      setActiveChatId(newChat.id);
      currentChatId = newChat.id;
    }

    const newMessages = [...messages, uploadMsg];
    setMessages(newMessages);

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (sessionId) {
        formData.append('session_id', sessionId);
      }

      const response = await fetch('/api/chatbot/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        // Store resume context
        setSessionId(data.session_id);
        setResumeId(data.resume_id);
        setResumeName(data.resume_name);

        // Update chat with resume info
        setChats(prev => prev.map(c =>
          c.id === currentChatId ? {
            ...c,
            sessionId: data.session_id,
            resumeId: data.resume_id,
            resumeName: data.resume_name,
          } : c
        ));

        const successMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || `✅ Đã xử lý thành công **${file.name}**`,
          taskType: 'upload',
        };

        const updatedMessages = [...newMessages, successMsg];
        setMessages(updatedMessages);
        setChats(prev => prev.map(c =>
          c.id === currentChatId ? { ...c, messages: updatedMessages } : c
        ));
      } else {
        const errorMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || `❌ Lỗi xử lý file: ${data.error}`,
        };

        const updatedMessages = [...newMessages, errorMsg];
        setMessages(updatedMessages);
        setChats(prev => prev.map(c =>
          c.id === currentChatId ? { ...c, messages: updatedMessages } : c
        ));
      }
    } catch (error) {
      console.error('Upload error:', error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '❌ Không thể kết nối đến server để tải file. Vui lòng thử lại.',
      };

      const updatedMessages = [...newMessages, errorMsg];
      setMessages(updatedMessages);
      setChats(prev => prev.map(c =>
        c.id === currentChatId ? { ...c, messages: updatedMessages } : c
      ));
    } finally {
      setIsUploading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestions = [
    'Xu hướng tuyển dụng IT 2025?',
    'Mức lương trung bình Data Engineer?',
    'Kỹ năng hot nhất hiện nay?',
    'Tư vấn CV cho fresher?',
  ];

  return (
    <div className="flex flex-col h-screen bg-[#f4f2ee]">
      {/* --- NAVBAR --- */}
      <nav className="flex justify-between items-center px-6 md:px-12 py-4 bg-white z-20 relative shadow-sm shrink-0">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center text-white">
            <BarChart2 size={24} className="text-blue-400" />
          </div>
          <span className="font-bold text-2xl text-slate-800">
            Career<span className="text-blue-600">Intel</span>
            <span className="block text-[10px] text-gray-500 font-normal -mt-1">Intelligent Job Market Hub</span>
          </span>
        </Link>

        <div className="hidden lg:flex items-center gap-8 font-semibold text-sm text-slate-800">
          <Link href="/search" className="hover:text-blue-600 transition">Job Search</Link>
          <Link href="#" className="hover:text-blue-600 transition">Market Insights</Link>
          <Link href="/ai" className="text-blue-600 border-b-2 border-blue-600 pb-1">AI Assistant</Link>
          <Link href="/profile" className="hover:text-blue-600 transition">My Profile</Link>
        </div>

        <div className="hidden lg:flex items-center gap-4 font-semibold text-sm text-slate-800">
          {user ? (
            <>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                  {user.user_metadata?.full_name?.charAt(0)?.toUpperCase() || user.email?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <span>Hi, {user.user_metadata?.full_name || 'User'}</span>
              </div>
              <button onClick={() => logout()} className="bg-gray-100 hover:bg-gray-200 text-slate-800 px-6 py-2.5 rounded-md font-medium transition shadow-sm cursor-pointer">
                Log Out
              </button>
            </>
          ) : (
            <>
              <Link href="/signup">
                <button className="bg-[#f27a42] hover:bg-[#e06830] text-white px-6 py-2.5 rounded-md font-medium transition shadow-md">Sign Up</button>
              </Link>
              <Link href="/login">
                <button className="bg-gray-100 hover:bg-gray-200 text-slate-800 px-6 py-2.5 rounded-md font-medium transition shadow-sm">Log In</button>
              </Link>
            </>
          )}
        </div>
      </nav>

      {/* --- BODY: SIDEBAR + CHAT AREA --- */}
      <div className="flex flex-1 overflow-hidden">

        {/* SIDEBAR */}
        <aside className="w-64 shrink-0 bg-white border-r border-gray-200 flex flex-col overflow-hidden">
          {/* New Chat + Search */}
          <div className="p-3 flex flex-col gap-2 border-b border-gray-100">
            <button
              onClick={handleNewChat}
              className="flex items-center gap-2 w-full px-3 py-2.5 rounded-lg text-slate-700 font-semibold text-sm hover:bg-[#f4f2ee] transition-colors"
            >
              <Plus size={18} className="text-blue-600" />
              New chat
            </button>
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[#f4f2ee] text-gray-500">
              <Search size={15} />
              <input
                type="text"
                placeholder="Search chats"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="bg-transparent outline-none text-sm w-full text-slate-700 placeholder-gray-400"
              />
            </div>
          </div>

          {/* Chat History */}
          <div className="flex-1 overflow-y-auto py-2">
            {filteredChats.length > 0 ? (
              <>
                <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider px-4 py-2">Recents</p>
                {filteredChats.map(chat => (
                  <div
                    key={chat.id}
                    onClick={() => handleSelectChat(chat.id)}
                    className={`group flex items-center justify-between gap-2 px-4 py-2.5 cursor-pointer rounded-lg mx-2 transition-colors ${
                      activeChatId === chat.id
                        ? 'bg-blue-50 text-blue-700'
                        : 'hover:bg-[#f4f2ee] text-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <MessageSquare size={15} className="shrink-0 text-gray-400" />
                      <span className="text-sm truncate">{chat.title}</span>
                    </div>
                    <button
                      onClick={e => handleDeleteChat(e, chat.id)}
                      className="shrink-0 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </>
            ) : (
              <p className="text-sm text-gray-400 text-center mt-8 px-4">No chat history found.</p>
            )}
          </div>
        </aside>

        {/* MAIN CHAT AREA */}
        <main className="flex-1 flex flex-col overflow-hidden bg-[#f4f2ee]">
          {/* Resume badge if one is loaded */}
          {resumeName && (
            <div className="px-6 pt-3">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-full text-xs text-blue-700">
                <FileText size={12} />
                <span className="font-medium">{resumeName}</span>
                <CheckCircle2 size={12} className="text-green-500" />
              </div>
            </div>
          )}

          {messages.length === 0 ? (
            /* Welcome Screen */
            <div className="flex-1 flex flex-col items-center justify-center px-6 gap-8">
              <div className="flex flex-col items-center gap-3 text-center">
                <div className="w-14 h-14 bg-white rounded-2xl shadow-md flex items-center justify-center border border-gray-100">
                  <Sparkles size={28} className="text-blue-500" />
                </div>
                <h1 className="text-3xl font-bold text-slate-800">Where should we begin?</h1>
                <p className="text-gray-500 text-sm max-w-md">
                  Ask me anything about the job market, recruitment trends, or career advice.
                  Upload your CV to get personalized feedback.
                </p>
              </div>

              {/* Suggestion chips */}
              <div className="grid grid-cols-2 gap-3 max-w-xl w-full">
                {suggestions.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => { setInputValue(s); }}
                    className="bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm text-slate-700 hover:border-blue-400 hover:bg-blue-50 hover:text-blue-700 transition-all text-left shadow-sm"
                  >
                    {s}
                  </button>
                ))}
              </div>

              {/* Input at center */}
              <div className="w-full max-w-2xl">
                <ChatInput
                  value={inputValue}
                  onChange={setInputValue}
                  onSend={handleSend}
                  onKeyDown={handleKeyDown}
                  onFileClick={() => fileInputRef.current?.click()}
                  isLoading={isTyping}
                  isUploading={isUploading}
                />
              </div>
            </div>
          ) : (
            /* Active Chat */
            <>
              <div className="flex-1 overflow-y-auto px-6 py-6 flex flex-col gap-4 max-w-3xl mx-auto w-full">
                {messages.map(msg => (
                  <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    {msg.role === 'assistant' && (
                      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0 mt-1">
                        <Sparkles size={16} className="text-white" />
                      </div>
                    )}
                    {msg.role === 'system' && (
                      <div className="w-8 h-8 rounded-full bg-amber-500 flex items-center justify-center shrink-0 mt-1">
                        <Loader2 size={16} className="text-white animate-spin" />
                      </div>
                    )}
                    <div
                      className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white rounded-br-sm'
                          : msg.role === 'system'
                          ? 'bg-amber-50 text-amber-800 border border-amber-200 rounded-bl-sm'
                          : 'bg-white text-slate-800 border border-gray-200 rounded-bl-sm'
                      }`}
                    >
                      <div
                        className="prose prose-sm max-w-none prose-headings:text-slate-800 prose-strong:text-slate-800 prose-code:text-blue-600 prose-code:bg-blue-50 prose-code:px-1 prose-code:rounded"
                        dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
                      />
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="flex gap-3 justify-start">
                    <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0 mt-1">
                      <Sparkles size={16} className="text-white" />
                    </div>
                    <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                      <div className="flex gap-1.5 items-center h-5">
                        <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:0ms]" />
                        <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:150ms]" />
                        <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:300ms]" />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input at bottom */}
              <div className="px-6 pb-6 max-w-3xl mx-auto w-full">
                <ChatInput
                  value={inputValue}
                  onChange={setInputValue}
                  onSend={handleSend}
                  onKeyDown={handleKeyDown}
                  onFileClick={() => fileInputRef.current?.click()}
                  isLoading={isTyping}
                  isUploading={isUploading}
                />
              </div>
            </>
          )}
        </main>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
        onChange={handleFileUpload}
        className="hidden"
      />
    </div>
  );
}


// ── ChatInput Component ─────────────────────────────────

function ChatInput({
  value,
  onChange,
  onSend,
  onKeyDown,
  onFileClick,
  isLoading,
  isUploading,
}: {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  onFileClick: () => void;
  isLoading?: boolean;
  isUploading?: boolean;
}) {
  return (
    <div className="flex items-center gap-3 bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
      <button
        onClick={onFileClick}
        disabled={isUploading}
        title="Tải lên CV (PDF/DOCX)"
        className="text-gray-400 hover:text-blue-600 shrink-0 transition-colors disabled:opacity-50"
      >
        {isUploading ? (
          <Loader2 size={18} className="animate-spin" />
        ) : (
          <Paperclip size={18} />
        )}
      </button>
      <textarea
        rows={1}
        value={value}
        onChange={e => onChange(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder={isUploading ? 'Đang xử lý file...' : 'Ask anything'}
        disabled={isUploading}
        className="flex-1 bg-transparent outline-none resize-none text-sm text-slate-800 placeholder-gray-400 leading-6 max-h-40 overflow-y-auto disabled:opacity-50"
      />
      <button
        onClick={onSend}
        disabled={!value.trim() || isLoading || isUploading}
        className="w-8 h-8 rounded-full bg-blue-600 disabled:bg-gray-200 flex items-center justify-center transition-colors hover:bg-blue-700 shrink-0"
      >
        {isLoading ? (
          <Loader2 size={14} className="text-white animate-spin" />
        ) : (
          <Send size={14} className={value.trim() ? 'text-white' : 'text-gray-400'} />
        )}
      </button>
    </div>
  );
}


// ── Simple Markdown Renderer ────────────────────────────

function renderMarkdown(text: string): string {
  if (!text) return '';

  let html = text
    // Escape HTML (but preserve our markdown transformations)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

    // Headers
    .replace(/^### (.+)$/gm, '<h3 class="text-base font-bold mt-4 mb-2">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-lg font-bold mt-4 mb-2">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="text-xl font-bold mt-4 mb-2">$1</h1>')

    // Bold and italic
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/~~(.+?)~~/g, '<del>$1</del>')

    // Inline code
    .replace(/`([^`]+)`/g, '<code class="text-xs bg-blue-50 text-blue-700 px-1 py-0.5 rounded">$1</code>')

    // Code blocks
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="bg-gray-900 text-gray-100 rounded-lg p-3 my-2 overflow-x-auto text-xs"><code>$2</code></pre>')

    // Blockquotes
    .replace(/^&gt; (.+)$/gm, '<blockquote class="border-l-4 border-blue-300 pl-3 my-2 text-gray-600 italic">$1</blockquote>')

    // Unordered lists
    .replace(/^(\s*)- (.+)$/gm, (_, indent, content) => {
      const level = indent.length >= 2 ? 'ml-4' : '';
      return `<li class="list-disc list-inside ${level} my-0.5">${content}</li>`;
    })

    // Horizontal rules
    .replace(/^---$/gm, '<hr class="my-4 border-gray-200" />')

    // Line breaks (double newline → paragraph break)
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>');

  return html;
}
