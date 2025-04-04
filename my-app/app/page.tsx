"use client";
import { useState, useRef, useEffect } from "react";

export default function VerifyInputForm() {
  const [inputText, setInputText] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    const formData = new FormData();
    if (inputText) formData.append("input_text", inputText);
    if (imageFile) formData.append("input_image", imageFile);

    try {
      const res = await fetch("http://10.102.196.135:8000/verify_input", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setResponse(data);
    } catch (err: any) {
      setError("Đã có lỗi xảy ra khi gửi yêu cầu");
    } finally {
      setLoading(false);
    }
  };

  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  const handlePaste = (e: React.ClipboardEvent) => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.type.indexOf("image") === 0) {
        const file = item.getAsFile();
        if (file) {
          setImageFile(file);
          const url = URL.createObjectURL(file);
          setPreviewUrl(url);
        }
      }
    }
  };

  const handleRemoveImage = () => {
    setImageFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
  };

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-white py-12 px-6">
      <div className="max-w-3xl mx-auto bg-white shadow-xl rounded-2xl p-10">
        <h1 className="text-3xl font-bold text-center text-blue-800 mb-6">
          Hệ thống xác thực thông tin FakeBuster
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Nhập thông tin cần kiểm chứng hoặc dán ảnh liên quan (ảnh chụp màn
          hình, ảnh tin giả...) để hệ thống giúp bạn xác thực.
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Văn bản cần kiểm chứng:
            </label>
            <textarea
              ref={textAreaRef}
              onPaste={handlePaste}
              className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={6}
              placeholder="Nhập hoặc dán đoạn văn bản, ảnh chụp màn hình vào đây để xác thực..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />

            {previewUrl && (
              <div className="mt-4 flex items-center gap-3 relative">
                <img
                  src={previewUrl}
                  alt="Ảnh đã dán"
                  className="w-20 h-20 rounded-xl object-cover border shadow-md"
                />
                <button
                  type="button"
                  onClick={handleRemoveImage}
                  className="absolute -top-2 -left-2 bg-red-600 text-white p-1 rounded-full shadow-md hover:bg-red-700"
                >
                  x
                </button>
                <span className="text-blue-600 text-sm truncate max-w-xs">
                  Đã dán ảnh: {imageFile?.name}
                </span>
              </div>
            )}
          </div>

          <div className="text-center">
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-xl shadow-lg transition duration-300"
              disabled={loading}
            >
              {loading ? "Đang xử lý..." : "Xác thực thông tin"}
            </button>
          </div>
        </form>

        {error && <p className="text-red-600 text-center mt-4">{error}</p>}

        {response && (
          <div className="mt-8 bg-gray-50 p-6 rounded-xl border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-3">
              Kết quả phản hồi:
            </h2>
            {response.input_text && (
              <p className="mb-2 truncate max-w-full">
                <span className="font-medium">Nội dung văn bản:</span>{" "}
                <span title={response.input_text}>{response.input_text}</span>
              </p>
            )}
            {response.input_image && (
              <p className="truncate max-w-full">
                <span className="font-medium">Tên file ảnh:</span>{" "}
                <span title={response.input_image}>{response.input_image}</span>
              </p>
            )}
            <p
              className="mt-3 italic text-green-600 truncate max-w-full"
              title={response.message}
            >
              {response.message}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
