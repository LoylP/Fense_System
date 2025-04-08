"use client";
import { useState, useRef, useEffect } from "react";

interface Star {
  id: number;
  left: string;
  top: string;
  size: number;
  opacity: number;
  delay: string;
}

interface VerifyResponse {
  input_text: string;
  input_image: string;
  message: string;
}

export default function VerifyInputForm() {
  const [inputText, setInputText] = useState<string>("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [response, setResponse] = useState<VerifyResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [stars, setStars] = useState<Star[]>([]);

  useEffect(() => {
    const generateStars = () => {
      const newStars: Star[] = [];
      for (let i = 0; i < 100; i++) {
        const size = Math.random() * 2 + 1;
        newStars.push({
          id: i,
          left: `${Math.random() * 100}%`,
          top: `${Math.random() * 100}%`,
          size,
          opacity: Math.random() * 0.8 + 0.2,
          delay: `${Math.random() * 5}s`
        });
      }
      setStars(newStars);
    };
    generateStars();
  }, []);

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
      const data: VerifyResponse = await res.json();
      setResponse(data);
    } catch {
      setError("Đã có lỗi xảy ra khi gửi yêu cầu");
    } finally {
      setLoading(false);
    }
  };

  const textAreaRef = useRef<HTMLTextAreaElement | null>(null);

  const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") === 0) {
        const file = items[i].getAsFile();
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
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
  };

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  return (
    <div className="min-h-screen bg-cover bg-center relative overflow-hidden" style={{ backgroundImage: "url('/bg_galaxy.gif')" }}>
      {/* Stars */}
      {stars.map((star) => (
        <div
          key={star.id}
          className="absolute bg-white rounded-full animate-twinkle"
          style={{
            left: star.left,
            top: star.top,
            width: `${star.size}px`,
            height: `${star.size}px`,
            opacity: star.opacity,
            animationDelay: star.delay,
          }}
        ></div>
      ))}

      {/* Centered Form */}
      <div className="min-h-screen flex justify-center items-center px-4">
        <div className="w-full max-w-4xl bg-black/70 backdrop-blur-md rounded-2xl p-12 border border-purple-500/20 shadow-2xl relative z-10 animate-fadeInUp">
          <h1 className="text-4xl text-center font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-fuchsia-300 to-blue-400 mb-8 animate-glow">
            FakeBuster - Hệ thống xác thực thông tin
          </h1>
          <p className="text-center text-blue-200 mb-2 text-lg">
            Nhập văn bản hoặc hình ảnh cần kiểm chứng vào bên dưới để hệ thống xử lý.
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <textarea
              ref={textAreaRef}
              onPaste={handlePaste}
              className="w-full border border-purple-500/30 rounded-lg p-4 bg-gray-900 text-white placeholder-purple-300/40 shadow-inner focus:outline-none focus:ring-2 focus:ring-purple-500/60 resize-none transition duration-300"
              rows={6}
              placeholder="Nhập hoặc dán nội dung cần xác thực..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />

            {previewUrl && (
              <div className="flex items-center gap-4 mt-2">
                <img src={previewUrl} alt="preview" className="w-20 h-20 object-cover rounded-xl border border-purple-400/40" />
                <button
                  type="button"
                  onClick={handleRemoveImage}
                  className="text-red-400 text-sm font-medium hover:underline"
                >
                  Xoá ảnh
                </button>
              </div>
            )}

            <div className="text-center">
              <button
                type="submit"
                disabled={loading}
                className={`inline-flex items-center justify-center px-8 py-3 text-white font-medium rounded-xl shadow-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 transition-transform transform hover:-translate-y-1 duration-300 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {loading ? (
                  <span className="flex items-center">
                    <span className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white mr-2"></span>
                    Đang xử lý...
                  </span>
                ) : (
                  "Xác thực thông tin"
                )}
              </button>
            </div>
          </form>

          {error && <p className="mt-4 text-red-400 text-center animate-fadeIn">{error}</p>}

          {response && (
            <div className="mt-6 bg-gray-900/70 p-4 rounded-lg text-blue-200 border border-purple-500/30 animate-fadeIn">
              <p><span className="text-purple-300">Văn bản:</span> {response.input_text}</p>
              <p><span className="text-purple-300">Ảnh:</span> {response.input_image}</p>
              <p className="italic text-green-400 mt-2">{response.message}</p>
            </div>
          )}
        </div>
      </div>

      <style jsx global>{`
        @keyframes fadeInUp {
          0% { opacity: 0; transform: translateY(20px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeInUp {
          animation: fadeInUp 0.8s ease-out forwards;
        }
        @keyframes twinkle {
          0%, 100% { opacity: 0.2; }
          50% { opacity: 1; }
        }
        .animate-twinkle {
          animation: twinkle 3s ease-in-out infinite;
        }
        @keyframes glow {
          0%, 100% { text-shadow: 0 0 10px #a855f7; }
          50% { text-shadow: 0 0 20px #7c3aed; }
        }
        .animate-glow {
          animation: glow 2.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
