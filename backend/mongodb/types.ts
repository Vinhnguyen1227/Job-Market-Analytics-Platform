import { ObjectId } from 'mongodb';

// ─────────────────────────────────────────────────────────────
// CV Attachment — metadata của file CV đính kèm vào message.
// File thực tế lưu trên Supabase Storage (bucket: user-cvs).
// MongoDB chỉ lưu reference để tránh duplicate data.
// ─────────────────────────────────────────────────────────────
export interface CvAttachment {
  /** Tên file gốc, VD: "NguyenVanA_CV.pdf" */
  fileName: string;
  /** Path trên Supabase Storage, VD: "user-id/1234567890_NguyenVanA_CV.pdf" */
  filePath: string;
  /** Kích thước file tính bằng bytes */
  fileSize: number;
  /** MIME type, VD: "application/pdf" | "application/msword" | ... */
  fileType: string;
  /** Supabase signed URL (expire 1 năm) — để AI/FE đọc được file */
  signedUrl: string;
  /** Thời điểm người dùng đính kèm file vào message */
  uploadedAt: Date;
}

// ─────────────────────────────────────────────────────────────
// Role của người gửi message
// ─────────────────────────────────────────────────────────────
export type MessageRole = 'user' | 'assistant' | 'system';

// ─────────────────────────────────────────────────────────────
// ChatMessage — một tin nhắn trong cuộc hội thoại.
// Được lưu dạng embedded array trong Conversation document.
// ─────────────────────────────────────────────────────────────
export interface ChatMessage {
  role: MessageRole;
  /** Nội dung text của tin nhắn */
  content: string;
  /** Thời điểm tạo message */
  createdAt: Date;
  /**
   * File CV đính kèm (optional).
   * Chỉ role 'user' mới có field này.
   */
  attachment?: CvAttachment | null;
  /**
   * Metadata phụ: tokens_used, model_version, latency_ms, v.v.
   * AI route sẽ điền sau khi nhận response từ model.
   */
  metadata?: Record<string, unknown>;
}

// ─────────────────────────────────────────────────────────────
// Conversation — một cuộc hội thoại.
// _id là ObjectId của MongoDB.
// userId là Supabase user UUID (string).
// ─────────────────────────────────────────────────────────────
export interface Conversation {
  _id: ObjectId;
  /** Supabase user UUID */
  userId: string;
  /** Tiêu đề cuộc hội thoại (auto-generate từ message đầu tiên) */
  title: string;
  /** Danh sách tin nhắn — embedded để đọc 1 query */
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
  /** Soft delete flag */
  isArchived: boolean;
}

// ─────────────────────────────────────────────────────────────
// DTO / input types
// ─────────────────────────────────────────────────────────────

/** Input để tạo message mới (không cần createdAt — service tự set) */
export interface NewMessageInput {
  role: MessageRole;
  content: string;
  attachment?: CvAttachment | null;
  metadata?: Record<string, unknown>;
}

/** Response trả về cho client (convert ObjectId → string) */
export interface ConversationResponse {
  id: string;
  userId: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
  isArchived: boolean;
}

/** Response danh sách (không kèm messages để nhẹ hơn) */
export interface ConversationListItem {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  isArchived: boolean;
  /** Số lượng message trong conversation */
  messageCount: number;
  /** Message cuối cùng (preview) */
  lastMessage?: Pick<ChatMessage, 'role' | 'content' | 'createdAt'>;
}
