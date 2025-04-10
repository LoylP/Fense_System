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
  input_image: string | null;
  message: string;
  verification_result: {
    raw: string;
  };
}

export default function VerifyInputForm() {
  const [inputText, setInputText] = useState<string>("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [response, setResponse] = useState<VerifyResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [stars, setStars] = useState<Star[]>([]);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    const newStars: Star[] = Array.from({ length: 100 }, (_, i) => ({
      id: i,
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      size: Math.random() * 2 + 1,
      opacity: Math.random() * 0.8 + 0.2,
      delay: `${Math.random() * 5}s`,
    }));
    setStars(newStars);
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
      const res = await fetch("http://10.102.196.135:8080/verify_input", {
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const handleUploadClick = () => fileInputRef.current?.click();

  const handleRemoveImage = () => {
    setImageFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  return (
    <div
      className="min-h-screen bg-cover bg-center relative overflow-hidden"
      style={{ backgroundImage: "url('/bg_galaxy.gif')" }}
    >
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

      <div className="min-h-screen flex justify-center items-center px-4">
        <div className="w-full max-w-4xl bg-black/70 backdrop-blur-md rounded-2xl p-12 border border-purple-500/20 shadow-2xl relative z-10 animate-fadeInUp">
          <h1 className="text-4xl text-center font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-fuchsia-300 to-blue-400 mb-8 animate-glow">
            FENSE - Hệ thống xác thực thông tin
          </h1>
          <p className="text-center text-blue-200 mb-2 text-lg">
            Nhập văn bản hoặc hình ảnh cần kiểm chứng vào bên dưới để hệ thống
            xử lý.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <textarea
              onPaste={handlePaste}
              className="w-full border border-purple-500/30 rounded-lg p-4 bg-gray-900 text-white placeholder-purple-300/40 shadow-inner focus:outline-none focus:ring-2 focus:ring-purple-500/60 resize-none transition duration-300"
              rows={response ? 2 : 6}
              placeholder="Nhập hoặc dán nội dung cần xác thực..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />

            {/* Preview ảnh gọn */}
            {previewUrl && (
              <div className="relative inline-block mt-2 animate-fadeIn">
                <img
                  src={previewUrl}
                  alt="preview"
                  className="w-16 h-16 object-cover rounded-lg border border-purple-400/40 shadow-md"
                />
                <button
                  type="button"
                  onClick={handleRemoveImage}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center shadow"
                >
                  ✕
                </button>
              </div>
            )}

            {/* Import + Submit buttons */}
            <div className="flex items-center justify-between mt-6">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/*"
                className="hidden"
              />
              <button
                type="button"
                onClick={handleUploadClick}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-800/60 hover:bg-indigo-700/80 text-blue-200 rounded-lg border border-purple-500/30 transition-all duration-300 transform hover:scale-105"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
              </button>

              <div className="flex-1 text-center">
                <button
                  type="submit"
                  disabled={loading}
                  className={`inline-flex items-center justify-center px-8 py-2 text-white font-semibold rounded-2xl shadow-xl bg-gradient-to-r from-purple-900 to-black hover:from-black hover:to-indigo-800 transition-transform transform hover:-translate-y-1 duration-300 ${
                    loading ? "opacity-60 cursor-wait" : ""
                  }`}
                >
                  {loading ? (
                    <span className="flex items-center gap-4">
                      <img
                        src="/Loader2.gif"
                        alt="Đang xử lý"
                        className="w-10 h-10 rounded-full border border-purple-400 shadow-xl"
                      />
                      <span className="text-lg text-purple-100 animate-pulse font-medium">
                        Đang xác thực...
                      </span>
                    </span>
                  ) : (
                    "Xác thực thông tin"
                  )}
                </button>
              </div>
            </div>
          </form>

          {error && (
            <p className="mt-4 text-red-400 text-center animate-fadeIn">
              {error}
            </p>
          )}

          {response?.verification_result?.raw && (
            <div className="mt-6 bg-gray-900/70 p-4 rounded-lg text-blue-200 border border-purple-500/30 animate-fadeIn">
              <h3 className="text-purple-300 font-semibold mb-2">
                🤖 Phân tích AI:
              </h3>
              {response.verification_result.raw
                .split(/(?=\d\. )/)
                .map((line, idx) => (
                  <p
                    key={idx}
                    className="mb-2 whitespace-pre-line leading-relaxed"
                  >
                    <span className="text-purple-400 font-semibold">
                      {line.trim().split(":")[0]}:
                    </span>{" "}
                    {line.split(":").slice(1).join(":").trim()}
                  </p>
                ))}
            </div>
          )}
        </div>
      </div>

      <style jsx global>{`
        @keyframes fadeInUp {
          0% {
            opacity: 0;
            transform: translateY(20px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeInUp {
          animation: fadeInUp 0.8s ease-out forwards;
        }
        @keyframes twinkle {
          0%,
          100% {
            opacity: 0.2;
          }
          50% {
            opacity: 1;
          }
        }
        .animate-twinkle {
          animation: twinkle 3s ease-in-out infinite;
        }
        @keyframes glow {
          0%,
          100% {
            text-shadow: 0 0 10px #a855f7;
          }
          50% {
            text-shadow: 0 0 20px #7c3aed;
          }
        }
        .animate-glow {
          animation: glow 2.5s ease-in-out infinite;
        }
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-in-out forwards;
        }
      `}</style>
    </div>
  );
}
