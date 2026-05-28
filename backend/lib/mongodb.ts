import { MongoClient } from 'mongodb';

const uri = process.env.MONGODB_URI;

if (!uri) {
  throw new Error('❌ LỖI HỆ THỐNG: Thiếu cấu hình MONGODB_URI trong biến môi trường! Vui lòng định nghĩa trong file .env.local hoặc thiết lập biến hệ thống.');
}
const options = {};

let client: MongoClient;
let clientPromise: Promise<MongoClient>;

const globalForMongo = global as unknown as { _mongoClientPromise: Promise<MongoClient> };

if (process.env.NODE_ENV === 'development') {
  if (!globalForMongo._mongoClientPromise) {
    client = new MongoClient(uri, options);
    globalForMongo._mongoClientPromise = client.connect();
  }
  clientPromise = globalForMongo._mongoClientPromise;
} else {
  client = new MongoClient(uri, options);
  clientPromise = client.connect();
}

export default clientPromise;
