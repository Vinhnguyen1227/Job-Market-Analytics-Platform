import { blacklistToken, isTokenBlacklisted } from './backend/lib/redisSecurity';

async function test() {
  console.log('=== KHỞI CHẠY KIỂM THỬ BẢO MẬT REDIS ===');
  
  // Dummy JWT với claim exp rất xa trong tương lai (năm 2061)
  const dummyToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjI4Nzg0NDAwMDB9.signature';
  
  console.log('\n1. Kiểm tra ban đầu: Token đã nằm trong blacklist chưa?');
  const initialCheck = await isTokenBlacklisted(dummyToken);
  console.log('-> Kết quả:', initialCheck ? 'ĐÃ BỊ CHẶN (LỖI)' : 'CHƯA BỊ CHẶN (ĐÚNG)');
  
  console.log('\n2. Giả lập người dùng Click Đăng xuất -> đưa Token vào danh sách đen...');
  await blacklistToken(dummyToken);
  
  console.log('\n3. Kiểm tra lại: Token đã bị chặn trong blacklist chưa?');
  const finalCheck = await isTokenBlacklisted(dummyToken);
  console.log('-> Kết quả:', finalCheck ? 'ĐÃ BỊ CHẶN (ĐÚNG)' : 'CHƯA BỊ CHẶN (LỖI)');
  
  if (!initialCheck && finalCheck) {
    console.log('\n✅ BÀI KIỂM THỬ THÀNH CÔNG RỰC RỠ! LỚP BẢO MẬT REDIS HOẠT ĐỘNG HOÀN HẢO!');
  } else {
    console.log('\n❌ BÀI KIỂM THỬ THẤT BẠI. CẦN KIỂM TRA LẠI KẾT NỐI REDIS.');
  }
  
  process.exit(0);
}

test().catch(err => {
  console.error('Lỗi chạy kiểm thử:', err);
  process.exit(1);
});
