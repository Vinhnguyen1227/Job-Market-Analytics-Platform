'use client';

import { useState } from 'react';

export default function KIEPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [progressMsg, setProgressMsg] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setProgressMsg('Đang tải file lên...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/kie', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();

      if (!data.job_id) {
        if (data.error) {
          setError(typeof data.error === 'string' ? data.error : 'Upload thất bại.');
        } else {
          setResult(data);
        }
        setLoading(false);
        return;
      }

      // Poll for completion (Option A: status route always HTTP 200).
      let attempts = 0;
      const maxAttempts = 150; // 2 s × 150 = 5 min

      const pollInterval = setInterval(async () => {
        attempts++;
        if (attempts === 30) {
          setProgressMsg('Đang chạy NER và embedding, vui lòng đợi...');
        }
        try {
          const statusRes = await fetch(`/api/chatbot/status/${data.job_id}`);
          const statusData = await statusRes.json();

          if (statusData.status === 'COMPLETED') {
            clearInterval(pollInterval);
            setResult(statusData.result);
            setLoading(false);
            setProgressMsg('');
          } else if (statusData.status === 'FAILED' || statusData.status === 'ERROR') {
            clearInterval(pollInterval);
            setError(statusData.error_message || statusData.error || 'Job failed');
            setLoading(false);
            setProgressMsg('');
          }
        } catch (err) {
          console.error('Polling error', err);
        }

        if (attempts >= maxAttempts) {
          clearInterval(pollInterval);
          setError('Quá thời gian xử lý (5 phút). Vui lòng thử lại với file nhỏ hơn.');
          setLoading(false);
          setProgressMsg('');
        }
      }, 2000);
    } catch (err: any) {
      console.error(err);
      setError(err?.message || 'Lỗi không xác định.');
      setLoading(false);
      setProgressMsg('');
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Key Information Extraction</h1>
      <form onSubmit={handleSubmit} className="mb-4">
        <input
          type="file"
          accept=".pdf,.docx,.png,.jpg,.jpeg"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="mb-2"
        />
        <button
          type="submit"
          disabled={!file || loading}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {loading ? (progressMsg || 'Processing...') : 'Extract Information'}
        </button>
      </form>
      {error && (
        <div className="bg-red-100 border border-red-300 text-red-700 p-3 rounded mb-4">
          {error}
        </div>
      )}
      {result && (
        <div className="bg-gray-100 p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">Extracted Information</h2>
          <pre className="text-xs overflow-auto max-h-[60vh]">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
