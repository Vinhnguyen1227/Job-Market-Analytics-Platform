import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

async function migrateAllJobs() {
  console.log('=== BẮT ĐẦU CHUẨN HÓA (CHẾ ĐỘ TỐC ĐỘ CHẬM - API FREE) ===');
  console.log('Lưu ý: Mất khoảng 8 giây cho mỗi bài đăng để không bị Google khóa.\n');

  const batchSize = 10; // Lấy từng mẻ nhỏ
  let totalProcessed = 0;
  let totalSuccess = 0;
  let totalFail = 0;

  while (true) {
    console.log(`Đang quét tìm các bài đăng bị lỗi "Khác" hoặc chưa chuẩn hóa...`);
    
    // Tìm các bài bị rỗng HOẶC bị lỗi thành chữ "Khác" do rớt mạng lúc nãy
    const { data: jobs, error } = await supabase
      .from('jobs')
      .select('*')
      .or('nganh_nghe_chuan_hoa.is.null,nganh_nghe_chuan_hoa.eq.Khác')
      .limit(batchSize);

    if (error) {
      console.error('Lỗi khi tải dữ liệu từ Supabase:', error.message);
      console.log('Chờ 10 giây rồi thử kết nối lại...');
      await new Promise(r => setTimeout(r, 10000));
      continue;
    }

    if (!jobs || jobs.length === 0) {
      console.log('\nTUYỆT VỜI! Đã chuẩn hóa xong 100% dữ liệu trong Database!');
      break;
    }

    console.log(`Đã tìm thấy ${jobs.length} bài cần sửa. Bắt đầu xử lý chậm...`);

    // Gửi từng job qua ML Server
    for (const job of jobs) {
      let retries = 3;
      let success = false;

      while (retries > 0 && !success) {
        try {
          const res = await fetch('http://127.0.0.1:8000/api/v1/jobs/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(job),
          });
          
          if (res.ok) {
            totalSuccess++;
            success = true;
          } else {
            const errorText = await res.text();
            console.error(`[Thất bại] Lỗi chuẩn hóa job ${job.url}:`, errorText);
            break; 
          }
        } catch (err) {
          retries--;
          console.error(`[Lỗi kết nối] ML Server bận. Đang thử lại...`);
          if (retries === 0) {
            totalFail++;
          } else {
            await new Promise(r => setTimeout(r, 5000));
          }
        }
      }
      
      totalProcessed++;
      console.log(`Tiến độ: Đã xử lý ${totalProcessed} jobs...`);

      // CHỐNG KHÓA CỔ HỌNG GOOGLE GEMINI (Giới hạn 15 req/phút)
      // Nghỉ 8 giây sau mỗi bài đăng
      await new Promise(r => setTimeout(r, 8000));
    }
  }

  console.log('\n=== HOÀN TẤT QUÁ TRÌNH CHUẨN HÓA ===');
  console.log(`Tổng số đã chạy hôm nay: ${totalProcessed}`);
  console.log(`Thành công: ${totalSuccess}`);
  console.log(`Thất bại: ${totalFail}`);
  console.log('Nếu bị đứng do hết 1500 lượt của ngày, hãy quay lại vào ngày mai và chạy tiếp lệnh này nhé!');
  process.exit(0);
}

migrateAllJobs().catch((err) => {
  console.error('Lỗi nghiêm trọng:', err);
  process.exit(1);
});
