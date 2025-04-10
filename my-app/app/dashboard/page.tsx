"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Dashboard() {
  const router = useRouter();
  const [urls, setUrls] = useState("");
  const [crawlMessage, setCrawlMessage] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const isLoggedIn = localStorage.getItem("isAdminLoggedIn");
    if (!isLoggedIn) {
      router.push("/admin");
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("isAdminLoggedIn");
    router.push("/");
  };

  const handleCrawlNews = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setCrawlMessage("");

    const urlList = urls
      .split("\n")
      .map((url) => url.trim())
      .filter((url) => url.length > 0);

    try {
      const response = await fetch("http://172.21.203.54:8000/pipeline_crawl_news", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ list_source: urlList }),
      });

      const data = await response.json();
      setCrawlMessage(data.message || "Đã xử lý xong!");
      setUrls("");
    } catch (error) {
      console.error("Lỗi crawl:", error);
      setCrawlMessage("❌ Có lỗi xảy ra khi crawl!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <aside className="bg-white shadow-lg h-screen w-64 fixed">
        <div className="p-6 h-full">
          <h1 className="text-3xl font-bold text-blue-800 mb-6">DASHBOARD</h1>
          <nav>
            <ul className="space-y-2">
              <li>
                <a href="/" className="block p-2 rounded-lg hover:bg-slate-200">Home</a>
              </li>
              <li>
                <a href="/dashboard" className="block p-2 bg-slate-300 rounded-lg hover:bg-slate-200">Dashboard</a>
              </li>
              <li>
                <a href="/news" className="block p-2 rounded-lg hover:bg-slate-200">News</a>
              </li>
              <li>
                <a href="/history" className="block p-2 rounded-lg hover:bg-slate-200">History</a>
              </li>
            </ul>
          </nav>
        </div>
      </aside>

      {/* Main */}
      <main className="ml-64 flex-1 p-6 relative">
        {/* Top right logout button */}
        <div className="absolute top-4 right-6">
          <button
            onClick={handleLogout}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded shadow"
          >
            Logout
          </button>
        </div>

        <h2 className="text-2xl font-semibold mb-6 text-center">
          📥 Crawl Tin Tức Từ Link URL
        </h2>

        {/* Form nhập link */}
        <div className="bg-white shadow rounded-lg p-6 max-w-3xl mx-auto">
          <form onSubmit={handleCrawlNews}>
            <label className="block text-gray-700 font-medium mb-2">
              Nhập danh sách link báo (mỗi link 1 dòng):
            </label>
            <textarea
              value={urls}
              onChange={(e) => setUrls(e.target.value)}
              rows={6}
              placeholder="https://dantri.com.vn/...\nhttps://vnexpress.net/..."
              className="w-full border border-gray-300 rounded-lg p-3 mb-4 focus:ring-blue-500 focus:border-blue-500"
            />

            <button
              type="submit"
              disabled={loading}
              className={`bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded transition-all ${
                loading ? "opacity-60 cursor-not-allowed" : ""
              }`}
            >
              {loading ? "Đang crawl..." : "Crawl tin tức"}
            </button>
          </form>

          {/* Loading indicator */}
          {loading && (
            <div className="mt-4 flex items-center gap-3 text-blue-700 font-medium">
              <svg className="animate-spin h-6 w-6 text-blue-700" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l4-4-4-4v4a8 8 0 00-8 8z" />
              </svg>
              Đang xử lý crawl dữ liệu, vui lòng chờ...
            </div>
          )}

          {/* Crawl result message */}
          {crawlMessage && !loading && (
            <p className="mt-4 text-blue-700 font-medium bg-blue-100 px-4 py-2 rounded shadow">
              {crawlMessage}
            </p>
          )}
        </div>
      </main>
    </div>
  );
}
