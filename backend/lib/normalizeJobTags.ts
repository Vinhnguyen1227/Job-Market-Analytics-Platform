/**
 * normalizeJobTags.ts
 * ───────────────────────────────────────────────────────────────
 * Chuẩn hóa tên skills/tags trong field `nganh_nghe`.
 *
 * Quy tắc:
 *  1. Ghép nhiều biến thể sai về 1 tên chuẩn (VD: "after effect" → "After Effects")
 *  2. Chuẩn hóa tên thương hiệu đúng chính tả (VD: "autocad" → "AutoCAD")
 *  3. Gộp các tag trùng nghĩa sau normalize để không bị lặp
 *  4. Loại bỏ tag quá ngắn (< 2 ký tự) hoặc rỗng
 */

// ─────────────────────────────────────────────────────────────
// BẢNG CHUẨN HÓA
// Key   : lowercase, đã strip whitespace (nhiều key → 1 value)
// Value : Tên hiển thị chuẩn
// ─────────────────────────────────────────────────────────────
const SKILL_MAP: Record<string, string> = {

  // ── Adobe Creative Suite ──────────────────────────────────
  'photoshop': 'Photoshop',
  'adobe photoshop': 'Photoshop',

  'illustrator': 'Adobe Illustrator',
  'adobe illustrator': 'Adobe Illustrator',
  'adobe illustration': 'Adobe Illustrator',   // sai chính tả phổ biến
  'ai (illustrator)': 'Adobe Illustrator',

  'after effect': 'After Effects',             // thiếu 's'
  'after effects': 'After Effects',
  'adobe after effects': 'After Effects',
  'ae': 'After Effects',

  'premiere': 'Adobe Premiere Pro',
  'premiere pro': 'Adobe Premiere Pro',
  'adobe premiere': 'Adobe Premiere Pro',
  'adobe premiere pro': 'Adobe Premiere Pro',
  'pr (premiere)': 'Adobe Premiere Pro',

  'indesign': 'Adobe InDesign',
  'adobe indesign': 'Adobe InDesign',
  'in design': 'Adobe InDesign',

  'adobe audition': 'Adobe Audition',
  'audition': 'Adobe Audition',

  'adobe xd': 'Adobe XD',
  'xd': 'Adobe XD',

  'lightroom': 'Adobe Lightroom',
  'adobe lightroom': 'Adobe Lightroom',

  // ── Thiết kế khác ─────────────────────────────────────────
  'canva': 'Canva',
  'figma': 'Figma',

  'sketchup': 'SketchUp',
  'sketch up': 'SketchUp',
  'sketch-up': 'SketchUp',

  'autocad': 'AutoCAD',
  'auto cad': 'AutoCAD',
  'auto-cad': 'AutoCAD',

  'revit': 'Revit',
  'autodesk revit': 'Revit',

  'etabs': 'ETABS',

  // ── Microsoft Office ──────────────────────────────────────
  'excel': 'Excel',
  'microsoft excel': 'Excel',
  'ms excel': 'Excel',

  'word': 'Word',
  'microsoft word': 'Word',
  'ms word': 'Word',

  'powerpoint': 'PowerPoint',
  'microsoft powerpoint': 'PowerPoint',
  'ms powerpoint': 'PowerPoint',
  'ppt': 'PowerPoint',

  'office': 'Microsoft Office',
  'microsoft office': 'Microsoft Office',
  'ms office': 'Microsoft Office',

  // ── Lập trình & Phần mềm ─────────────────────────────────
  'python': 'Python',
  'sql': 'SQL',
  'reactjs': 'ReactJS',
  'react': 'ReactJS',
  'react.js': 'ReactJS',
  'flutter': 'Flutter',
  'android': 'Android',
  'ios': 'iOS',
  'php': 'PHP',
  'java': 'Java',
  'javascript': 'JavaScript',
  'js': 'JavaScript',
  'typescript': 'TypeScript',
  'ts': 'TypeScript',
  'nodejs': 'Node.js',
  'node.js': 'Node.js',
  'node js': 'Node.js',
  'c#': 'C#',
  'c++': 'C++',
  'git': 'Git',
  'docker': 'Docker',
  'erp': 'ERP',
  'sap': 'SAP',
  'misa': 'MISA',
  'plc': 'PLC',
  'cisco': 'Cisco',

  // ── Quản lý & Phương pháp ─────────────────────────────────
  'iso': 'ISO',
  'lean': 'Lean',
  'kaizen': 'Kaizen',
  '5s': '5S',
  'kpi': 'KPI',
  'hse': 'HSE',
  'pccc': 'PCCC',

  // ── Kỹ năng ngôn ngữ ─────────────────────────────────────
  'tiếng anh': 'Tiếng Anh',
  'tiếng anh thành thạo': 'Tiếng Anh',          // gộp về 1
  'english': 'Tiếng Anh',
  'tiếng trung': 'Tiếng Trung',
  'tiếng nhật': 'Tiếng Nhật',
  'tiếng hàn': 'Tiếng Hàn',
  'tiếng hàn quốc': 'Tiếng Hàn',
  'bằng lái': 'Bằng Lái',

  // ── Mạng xã hội / Digital Marketing ──────────────────────
  'facebook': 'Facebook',
  'tiktok': 'TikTok',
  'tik tok': 'TikTok',
  'youtube': 'YouTube',
  'you tube': 'YouTube',
  'zalo': 'Zalo',
  'google': 'Google',
  'seo': 'SEO',
  'google ads': 'Google Ads',
  'facebook ads': 'Facebook Ads',
  'shopee': 'Shopee',
  'fanpage': 'Fanpage',
  'website': 'Website',
  'online': 'Online',
  'internet': 'Internet',
  'wifi': 'WiFi',
  'email': 'Email Marketing',
  'social': 'Social Media',
  'content': 'Content',
  'tổng đài': 'Tổng Đài',
  'communication': 'Communication',

  // ── Kế toán / Tài chính (chi tiết) ──────────────────────
  'hạch toán': 'Hạch Toán',
  'báo cáo thuế': 'Báo Cáo Thuế',
  'báo cáo tài chính': 'Báo Cáo Tài Chính',
  'quyết toán thuế': 'Quyết Toán Thuế',
  'quy trình kế toán': 'Quy Trình Kế Toán',
  'phần mềm kế toán': 'Phần Mềm Kế Toán',
  'hóa đơn': 'Hóa Đơn',
  'chứng từ': 'Chứng Từ',
  'công nợ': 'Công Nợ',
  'chi phí': 'Chi Phí',
  'chi phí nhân sự': 'Chi Phí Nhân Sự',
  'ngân sách': 'Ngân Sách',
  'dòng tiền': 'Dòng Tiền',
  'tài sản': 'Tài Sản',
  'vốn': 'Vốn',
  'thuế': 'Thuế',
  'số liệu kế toán': 'Số Liệu Kế Toán',
  'audit': 'Audit',
  'pháp lý': 'Pháp Lý',
  'hợp đồng lao động': 'Hợp Đồng Lao Động',
  'luật lao động': 'Luật Lao Động',
  'chứng chỉ an toàn lao động': 'Chứng Chỉ An Toàn Lao Động',

  // ── HR / Sales / Marketing ────────────────────────────────
  'doanh số': 'Doanh Số',
  'khách hàng cá nhân': 'Khách Hàng Cá Nhân',
  'khách hàng doanh nghiệp': 'Khách Hàng Doanh Nghiệp',
  'nghiên cứu thị trường': 'Nghiên Cứu Thị Trường',
  'hàng tiêu dùng': 'Hàng Tiêu Dùng',
  'tiêu dùng': 'Tiêu Dùng',
  'fmcg': 'FMCG',
  'b2b': 'B2B',

  // ── Kỹ thuật / IT ────────────────────────────────────────
  'kỹ thuật': 'Kỹ Thuật',
  'hệ thống mạng': 'Hệ Thống Mạng',
  'backend': 'Backend',
  'mobile': 'Mobile',
  'ux': 'UX/UI',
  'designer': 'Designer',
  'product manager': 'Product Manager',
  'team leader': 'Team Leader',
  'manager': 'Manager',
  'technical': 'Technical',
  'software engineering': 'Software Engineering',

  // ── Vận hành / Kho ───────────────────────────────────────
  'kho': 'Kho',
  'vật tư': 'Vật Tư',
  'packing list': 'Packing List',
  'pos': 'POS',
  'vệ sinh an toàn thực phẩm': 'Vệ Sinh An Toàn Thực Phẩm',

  // ── Ngành nghề chính ─────────────────────────────────────
  'kế toán': 'Kế Toán',
  'kiểm toán': 'Kiểm Toán',
  'tài chính': 'Tài Chính',
  'tài chính - ngân hàng': 'Tài Chính - Ngân Hàng',
  'ngân hàng': 'Ngân Hàng',
  'bất động sản': 'Bất Động Sản',
  'bđs': 'Bất Động Sản',
  'logistics': 'Logistics',
  'xuất nhập khẩu': 'Xuất Nhập Khẩu',
  'cntt': 'CNTT',
  'phần mềm': 'Phần Mềm',
  'xây dựng': 'Xây Dựng',
  'kiến trúc': 'Kiến Trúc',
  'nội thất': 'Nội Thất',
  'thời trang': 'Thời Trang',
  'thực phẩm': 'Thực Phẩm',
  'dược': 'Dược',
  'y tế': 'Y Tế',
  'nha khoa': 'Nha Khoa',
  'giáo dục': 'Giáo Dục',
  'nhà hàng': 'Nhà Hàng',
  'khách sạn': 'Khách Sạn',
  'du lịch': 'Du Lịch',
  'vận tải': 'Vận Tải',
  'nông nghiệp': 'Nông Nghiệp',
  'chứng khoán': 'Chứng Khoán',
  'sản xuất': 'Sản Xuất',
  'cơ khí': 'Cơ Khí',
  'điện tử': 'Điện Tử',
  'viễn thông': 'Viễn Thông',
  'thương mại điện tử': 'Thương Mại Điện Tử',
  'bảo hiểm': 'Bảo Hiểm',
  'dệt may': 'Dệt May',
  'hóa chất': 'Hóa Chất',
  'năng lượng mặt trời': 'Năng Lượng Mặt Trời',
  'in ấn': 'In Ấn',
  'spa': 'Spa',
  'làm đẹp': 'Làm Đẹp',
  'thẩm mỹ': 'Thẩm Mỹ',
  'chăm sóc sức khỏe': 'Chăm Sóc Sức Khỏe',
  'siêu thị': 'Siêu Thị',
  'chuỗi cửa hàng': 'Chuỗi Cửa Hàng',
  'nhà phân phối': 'Nhà Phân Phối',
  'đại lý': 'Đại Lý',
  'du học': 'Du Học',
  'tuyển sinh': 'Tuyển Sinh',
  'sự kiện': 'Sự Kiện',
  'bảo vệ': 'Bảo Vệ',
  'lâm nghiệp': 'Lâm Nghiệp',
  'mỹ phẩm': 'Mỹ Phẩm',
  'vlxd': 'VLXD',
  'ô tô': 'Ô Tô',
  'f&b': 'F&B',
};

// ─────────────────────────────────────────────────────────────
// Capitalize first letter of each word
// ─────────────────────────────────────────────────────────────
function toTitleCase(str: string): string {
  return str.replace(
    /\w\S*/g,
    (txt) => txt.charAt(0).toUpperCase() + txt.substring(1).toLowerCase()
  );
}

// ─────────────────────────────────────────────────────────────
// Normalize 1 tag đơn lẻ
// ─────────────────────────────────────────────────────────────
function normalizeSingleTag(raw: string): string | null {
  const key = raw.trim().toLowerCase().replace(/\s+/g, ' ');
  if (!key || key.length < 2) return null;

  // Bỏ qua các tag rác
  const excludeTags = ['khuôn ép nhựa', 'quà tặng', 'tai mũi họng', 'topic 4'];
  if (excludeTags.includes(key)) return null;

  // 1. Gộp theo Partial Match (chứa từ khóa) - Ưu tiên cao nhất
  if (key.includes('kế toán')) return 'Kế Toán';
  if (key.includes('kinh doanh')) return 'Kinh Doanh';
  if (key.includes('bảo hiểm')) return 'Bảo Hiểm';
  if (key.includes('bếp')) return 'Bếp';
  if (key.includes('luật')) return 'Luật';
  if (key.includes('facebook')) return 'Facebook';
  if (key.includes('google')) return 'Google';
  if (key.includes('mẹ và bé') || key.includes('mẹ & bé')) return 'Mẹ & Bé';
  if (
    key.includes('lái xe') ||
    key.includes('bằng b2') ||
    key.includes('hạng b2') ||
    key.includes('bằng c') ||
    key.includes('hạng c') ||
    key.includes('tài xế') ||
    key.includes('bằng lái')
  ) {
    return 'Lái Xe';
  }

  // 2. Tra trong bảng Map cứng
  if (SKILL_MAP[key]) return SKILL_MAP[key];

  // 3. Không có trong bảng → chuẩn hóa Title Case (viết hoa chữ cái đầu)
  // Lưu ý regex của toTitleCase có thể bị lỗi với các ký tự tiếng Việt có dấu, 
  // nên ta có thể dùng hàm thủ công.
  const titleCased = key.split(' ').map(word => {
    return word.charAt(0).toUpperCase() + word.slice(1);
  }).join(' ');

  return titleCased;
}

// ─────────────────────────────────────────────────────────────
// normalizeJobTags — hàm chính
// Input : chuỗi tags phân cách bằng dấu phẩy
//         VD: "after effect, Auto Cad, illustrator, tiếng anh thành thạo"
// Output: chuỗi đã chuẩn hóa, không trùng lặp
//         VD: "After Effects, AutoCAD, Adobe Illustrator, Tiếng Anh"
// ─────────────────────────────────────────────────────────────
export function normalizeJobTags(raw: string | null | undefined): string {
  if (!raw || raw.trim() === '' || raw.trim().toUpperCase() === 'N/A') {
    return 'N/A';
  }

  const seen = new Set<string>();
  const normalized: string[] = [];

  for (const part of raw.split(',')) {
    const tag = normalizeSingleTag(part);
    if (!tag) continue;

    // Lowercase để so sánh dedup (tránh "After Effects" & "after effects" bị lặp)
    const dedupeKey = tag.toLowerCase();
    if (seen.has(dedupeKey)) continue;

    seen.add(dedupeKey);
    normalized.push(tag);
  }

  return normalized.length > 0 ? normalized.join(', ') : 'N/A';
}

/**
 * Trả về danh sách canonical names đã biết.
 * Dùng cho UI filter, autocomplete, v.v.
 */
export function getCanonicalSkillNames(): string[] {
  return [...new Set(Object.values(SKILL_MAP))].sort();
}

export default normalizeJobTags;
