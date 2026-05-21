import { MongoClient, Db } from 'mongodb';

const MONGODB_URI = process.env.MONGODB_URI!;
const DB_NAME = 'job_market_analytics';

if (!MONGODB_URI) {
  throw new Error(
    '[MongoDB] MONGODB_URI chưa được cấu hình trong .env.local'
  );
}

// ─────────────────────────────────────────────────────────────
// Singleton pattern — tránh tạo nhiều connection trong Next.js
// dev mode (hot reload sẽ tạo lại module nhiều lần).
// Dùng globalThis để giữ instance tồn tại qua các hot reloads.
// ─────────────────────────────────────────────────────────────
declare global {
  // eslint-disable-next-line no-var
  var _mongoClient: MongoClient | undefined;
  // eslint-disable-next-line no-var
  var _mongoClientPromise: Promise<MongoClient> | undefined;
}

let clientPromise: Promise<MongoClient>;

if (process.env.NODE_ENV === 'development') {
  // Trong development: tái dùng connection qua globalThis
  if (!global._mongoClientPromise) {
    const client = new MongoClient(MONGODB_URI);
    global._mongoClient = client;
    global._mongoClientPromise = client.connect();
  }
  clientPromise = global._mongoClientPromise!;
} else {
  // Trong production: tạo connection mới cho mỗi module instance
  const client = new MongoClient(MONGODB_URI);
  clientPromise = client.connect();
}

/**
 * Trả về Db instance đã kết nối.
 * Gọi hàm này bất cứ lúc nào cần truy cập MongoDB.
 *
 * @example
 * const db = await getDb();
 * const col = db.collection('conversations');
 */
export async function getDb(): Promise<Db> {
  const client = await clientPromise;
  return client.db(DB_NAME);
}

export default clientPromise;
