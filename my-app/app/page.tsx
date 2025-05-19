"use client";

import { useState, useRef, useEffect } from "react";
import API_BASE_URL from "../lib/api";

interface Star {
  id: number;
  left: string;
  top: string;
  size: number;
  opacity: number;
  delay: string;
}

interface TtpMatch {
  category: string;
  ttp: string;
  source: string;
}

interface VerifyResponse {
  input_text: string;
  input_image: string | null;
  message: string;
  verification_result: {
    raw: string;
  };
  ttp_matches?: TtpMatch[];
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
      const res = await fetch(`${API_BASE_URL}/verify_input`, {
        method: "POST",
        body: formData,
      });
      const data: VerifyResponse = await res.json();
      setResponse(data);
    } catch {
      setError(
        "\u0110\u00e3 c\u00f3 l\u1ed7i x\u1ea3y ra khi g\u1eedi y\u00eau c\u1ea7u"
      );
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
    <div className="min-h-screen bg-gradient-to-tr from-gray-900 via-blue-900 to-black relative overflow-hidden">
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute top-0 left-0 w-full h-full object-cover brightness-75 contrast-110"
        src="/bg2.mov"
      />
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
        />
      ))}

      <div className="min-h-screen flex justify-center items-start gap-8 px-4 relative z-10 py-12 flex-wrap md:flex-nowrap">
        <div className="flex-1 max-w-2xl bg-black/80 backdrop-blur-md rounded-2xl p-8 border border-blue-600/60 shadow-md relative z-20">
          <h1 className="text-3xl text-center font-bold text-white mb-6 tracking-wide">
            FENSE - Hệ thống xác thực thông tin
          </h1>
          <p className="text-center text-blue-400 mb-4 text-base">
            Nhập văn bản hoặc hình ảnh cần kiểm chứng vào bên dưới để hệ thống
            xử lý.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <textarea
              onPaste={handlePaste}
              className="w-full border border-blue-600 rounded-lg p-3 bg-gray-900 text-white placeholder-blue-400 shadow-inner focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y transition duration-300 max-h-48"
              rows={response ? 3 : 5}
              placeholder="Nhập hoặc dán nội dung cần xác thực..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />

            {previewUrl && (
              <div className="relative inline-block mt-2 animate-fadeIn">
                <img
                  src={previewUrl}
                  alt="preview"
                  className="w-14 h-14 object-cover rounded-lg border border-blue-600 shadow-md"
                />
                <button
                  type="button"
                  onClick={handleRemoveImage}
                  className="absolute -top-2 -right-2 bg-red-600 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center shadow-lg hover:bg-red-700 transition"
                >
                  ✕
                </button>
              </div>
            )}

            <div className="flex justify-between items-center mt-6 gap-3 flex-wrap">
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
                className="flex items-center gap-2 px-3 py-2 bg-blue-800/70 hover:bg-blue-700 text-blue-200 rounded-lg border border-blue-600 transition-all duration-300 transform hover:scale-105 shadow-md"
              >
                📁
              </button>

              <div className="flex justify-center w-full mt-3 md:mt-0">
                <button
                  type="submit"
                  disabled={loading}
                  className={`inline-flex items-center justify-center px-6 py-2 text-white font-semibold rounded-2xl shadow-md bg-gradient-to-r from-blue-900 to-indigo-900 hover:from-indigo-900 hover:to-blue-900 transition-transform transform hover:-translate-y-1 duration-300 ${
                    loading ? "opacity-60 cursor-wait" : ""
                  }`}
                >
                  {loading ? (
                    <span className="flex items-center gap-3">
                      <img
                        src="/Loader2.gif"
                        alt="Đang xử lý"
                        className="w-8 h-8 rounded-full border border-blue-600 shadow-md"
                      />
                      <span className="text-blue-300 animate-pulse font-medium text-sm">
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
            <p className="mt-3 text-red-500 text-center animate-fadeIn text-sm">
              {error}
            </p>
          )}

          {response?.verification_result?.raw && (
            <div className="mt-6 bg-gray-900/90 p-4 rounded-lg text-blue-300 border border-blue-700 shadow-md animate-fadeIn whitespace-pre-wrap max-h-[300px] overflow-y-auto">
              <h3 className="text-blue-400 font-semibold mb-2 text-sm">
                🤖 Phân tích AI:
              </h3>
              {response.verification_result.raw
                .split(/(?=\d\. )/)
                .map((line, idx) => (
                  <p key={idx} className="mb-1 leading-relaxed text-sm">
                    <span className="text-blue-500 font-semibold">
                      {line.trim().split(":")[0]}:
                    </span>{" "}
                    {line.split(":").slice(1).join(":").trim()}
                  </p>
                ))}
            </div>
          )}
        </div>

        {response?.ttp_matches && response.ttp_matches.length > 0 && (
          <div className="w-full md:w-[420px] bg-slate-800/40 p-6 rounded-lg text-white border border-blue-600 shadow-md max-h-[400px] overflow-y-auto sticky top-[20%] z-20">
            <h3 className="text-white font-semibold mb-4 text-base">
              ⚠️ TTP Mapping:
            </h3>
            <ul className="space-y-5 text-sm">
              {response.ttp_matches.map((ttp, idx) => (
                <li
                  key={idx}
                  className="border border-blue-700 rounded-md p-3 bg-blue-900/80 hover:bg-blue-400/50 transition cursor-pointer"
                >
                  <p>
                    <strong>Category:</strong> {ttp.category}
                  </p>
                  <p>
                    <strong>TTP:</strong> {ttp.ttp}
                  </p>
                  <p>
                    <strong>Source:</strong>{" "}
                    <a
                      href={ttp.source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:underline"
                    >
                      {ttp.source}
                    </a>
                  </p>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <style jsx global>{`
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
