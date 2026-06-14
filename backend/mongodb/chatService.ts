import { ObjectId, Collection } from 'mongodb';
import { getDb } from './client';
import type {
  Conversation,
  ConversationResponse,
  ConversationListItem,
  NewMessageInput,
  ChatMessage,
} from './types';

export type { MessageRole } from './types';

const COLLECTION = 'conversations';

// ─────────────────────────────────────────────────────────────
// Helper: lấy collection + đảm bảo indexes đã được tạo
// Indexes chỉ tạo 1 lần (MongoDB idempotent với createIndex).
// ─────────────────────────────────────────────────────────────
async function getCollection(): Promise<Collection<Conversation>> {
  const db = await getDb();
  const col = db.collection<Conversation>(COLLECTION);

  // Tạo indexes (chạy background, idempotent)
  await Promise.all([
    col.createIndex({ userId: 1 }),
    col.createIndex({ updatedAt: -1 }),
    col.createIndex({ isArchived: 1 }),
  ]);

  return col;
}

// ─────────────────────────────────────────────────────────────
// Helper: convert document → response DTO
// ─────────────────────────────────────────────────────────────
function toResponse(doc: Conversation): ConversationResponse {
  return {
    id: doc._id.toHexString(),
    userId: doc.userId,
    title: doc.title,
    messages: doc.messages,
    createdAt: doc.createdAt,
    updatedAt: doc.updatedAt,
    sessionId: doc.sessionId,
    isArchived: doc.isArchived,
  };
}

function toListItem(doc: Conversation): ConversationListItem {
  const lastMessage =
    doc.messages.length > 0
      ? doc.messages[doc.messages.length - 1]
      : undefined;

  return {
    id: doc._id.toHexString(),
    title: doc.title,
    createdAt: doc.createdAt,
    updatedAt: doc.updatedAt,
    sessionId: doc.sessionId,
    isArchived: doc.isArchived,
    messageCount: doc.messages.length,
    lastMessage: lastMessage
      ? {
          role: lastMessage.role,
          content: lastMessage.content,
          createdAt: lastMessage.createdAt,
        }
      : undefined,
  };
}

// ─────────────────────────────────────────────────────────────
// Helper: sinh title tự động từ message đầu tiên
// ─────────────────────────────────────────────────────────────
function generateTitle(firstMessageContent?: string): string {
  if (!firstMessageContent) return 'Cuộc hội thoại mới';
  return firstMessageContent.length > 60
    ? firstMessageContent.slice(0, 60).trimEnd() + '…'
    : firstMessageContent;
}

// ─────────────────────────────────────────────────────────────
// createConversation
// Tạo conversation mới, optionally kèm message đầu tiên.
// ─────────────────────────────────────────────────────────────
export async function createConversation(
  userId: string,
  firstMessage?: NewMessageInput
): Promise<ConversationResponse> {
  const col = await getCollection();
  const now = new Date();

  const messages: ChatMessage[] = firstMessage
    ? [{ ...firstMessage, createdAt: now }]
    : [];

  const doc: Omit<Conversation, '_id'> = {
    userId,
    title: generateTitle(firstMessage?.content),
    messages,
    createdAt: now,
    updatedAt: now,
    isArchived: false,
  };

  const result = await col.insertOne(doc as Conversation);

  return toResponse({ _id: result.insertedId, ...doc } as Conversation);
}

// ─────────────────────────────────────────────────────────────
// getConversation
// Lấy 1 conversation. Trả về null nếu không tìm thấy
// hoặc userId không khớp (ownership check).
// ─────────────────────────────────────────────────────────────
export async function getConversation(
  conversationId: string,
  userId: string
): Promise<ConversationResponse | null> {
  if (!ObjectId.isValid(conversationId)) return null;

  const col = await getCollection();
  const doc = await col.findOne({
    _id: new ObjectId(conversationId),
    userId,
    isArchived: false,
  });

  return doc ? toResponse(doc) : null;
}

// ─────────────────────────────────────────────────────────────
// listConversations
// Lấy danh sách conversations của user (không kèm toàn bộ messages).
// Sắp xếp theo updatedAt mới nhất trước.
// ─────────────────────────────────────────────────────────────
export async function listConversations(
  userId: string,
  limit = 20,
  skip = 0
): Promise<ConversationListItem[]> {
  const col = await getCollection();

  const docs = await col
    .find({ userId, isArchived: false })
    .sort({ updatedAt: -1 })
    .skip(skip)
    .limit(limit)
    .toArray();

  return docs.map(toListItem);
}

// ─────────────────────────────────────────────────────────────
// appendMessage
// Thêm 1 message vào cuối conversation.
// Message có thể kèm CvAttachment (optional).
// Trả về null nếu conversation không tồn tại / không thuộc user.
// ─────────────────────────────────────────────────────────────
export async function appendMessage(
  conversationId: string,
  userId: string,
  message: NewMessageInput
): Promise<ConversationResponse | null> {
  if (!ObjectId.isValid(conversationId)) return null;

  const col = await getCollection();
  const now = new Date();
  const newMessage: ChatMessage = { ...message, createdAt: now };

  const result = await col.findOneAndUpdate(
    { _id: new ObjectId(conversationId), userId, isArchived: false },
    {
      $push: { messages: newMessage },
      $set: { updatedAt: now },
    },
    { returnDocument: 'after' }
  );

  return result ? toResponse(result) : null;
}

// ─────────────────────────────────────────────────────────────
// appendMessages
// Thêm nhiều messages cùng lúc (VD: user message + assistant reply).
// ─────────────────────────────────────────────────────────────
export async function appendMessages(
  conversationId: string,
  userId: string,
  messages: NewMessageInput[]
): Promise<ConversationResponse | null> {
  if (!ObjectId.isValid(conversationId) || messages.length === 0) return null;

  const col = await getCollection();
  const now = new Date();
  const newMessages: ChatMessage[] = messages.map((m) => ({
    ...m,
    createdAt: now,
  }));

  const result = await col.findOneAndUpdate(
    { _id: new ObjectId(conversationId), userId, isArchived: false },
    {
      $push: { messages: { $each: newMessages } },
      $set: { updatedAt: now },
    },
    { returnDocument: 'after' }
  );

  return result ? toResponse(result) : null;
}

// ─────────────────────────────────────────────────────────────
// updateConversationTitle
// Cập nhật title của conversation.
// ─────────────────────────────────────────────────────────────
export async function updateConversationTitle(
  conversationId: string,
  userId: string,
  title: string
): Promise<ConversationResponse | null> {
  if (!ObjectId.isValid(conversationId)) return null;

  const col = await getCollection();
  const now = new Date();

  const result = await col.findOneAndUpdate(
    { _id: new ObjectId(conversationId), userId, isArchived: false },
    { $set: { title: title.trim(), updatedAt: now } },
    { returnDocument: 'after' }
  );

  return result ? toResponse(result) : null;
}

// ─────────────────────────────────────────────────────────────
// updateSessionId
// Liên kết FastAPI session_id vào conversation.
// ─────────────────────────────────────────────────────────────
export async function updateSessionId(
  conversationId: string,
  userId: string,
  sessionId: string
): Promise<ConversationResponse | null> {
  if (!ObjectId.isValid(conversationId)) return null;

  const col = await getCollection();
  const now = new Date();

  const result = await col.findOneAndUpdate(
    { _id: new ObjectId(conversationId), userId, isArchived: false },
    { $set: { sessionId: sessionId.trim(), updatedAt: now } },
    { returnDocument: 'after' }
  );

  return result ? toResponse(result) : null;
}

// ─────────────────────────────────────────────────────────────
// deleteConversation
// Xóa vĩnh viễn conversation (hard delete).
// ─────────────────────────────────────────────────────────────
export async function deleteConversation(
  conversationId: string,
  userId: string
): Promise<boolean> {
  if (!ObjectId.isValid(conversationId)) return false;

  const col = await getCollection();
  const result = await col.deleteOne({
    _id: new ObjectId(conversationId),
    userId,
  });

  return result.deletedCount === 1;
}

// ─────────────────────────────────────────────────────────────
// archiveConversation
// Soft delete — đánh dấu isArchived = true.
// ─────────────────────────────────────────────────────────────
export async function archiveConversation(
  conversationId: string,
  userId: string
): Promise<boolean> {
  if (!ObjectId.isValid(conversationId)) return false;

  const col = await getCollection();
  const result = await col.updateOne(
    { _id: new ObjectId(conversationId), userId },
    { $set: { isArchived: true, updatedAt: new Date() } }
  );

  return result.modifiedCount === 1;
}
