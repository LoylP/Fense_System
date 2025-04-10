"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface NewsItem {
  id: string;
  title: string;
  content: string;
  date: string;
  source: string;
}

export default function NewsPage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const isLoggedIn = localStorage.getItem("isAdminLoggedIn");
    if (!isLoggedIn) {
      router.push("/admin");
    } else {
      fetchNews();
    }
  }, []);

  const fetchNews = async () => {
    try {
      const res = await fetch("http://172.21.203.54:8000/get_news");
      const data = await res.json();
      setNews(data.data || []);
    } catch (err) {
      console.error("Lỗi khi lấy tin tức:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("isAdminLoggedIn");
    router.push("/");
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
                <a href="/dashboard" className="block p-2 rounded-lg hover:bg-slate-200">Dashboard</a>
              </li>
              <li>
                <a href="/news" className="block p-2 bg-slate-300 rounded-lg">News</a>
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
        {/* Logout */}
        <div className="absolute top-4 right-6">
          <button
            onClick={handleLogout}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded shadow"
          >
            Logout
          </button>
        </div>

        <h2 className="text-2xl font-semibold mb-6 text-center">
          📰 Danh sách bài báo đã crawl
        </h2>

        {loading ? (
          <div className="flex justify-center mt-10">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-700"></div>
          </div>
        ) : (
          <div className="bg-white shadow rounded-lg overflow-x-auto p-6">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Tiêu đề</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Ngày</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Nguồn</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Nội dung</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {news.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center py-6 text-gray-500">
                      Không có bài viết nào.
                    </td>
                  </tr>
                ) : (
                  news.map((item, index) => (
                    <tr key={index} className="text-sm text-gray-700">
                      <td className="px-4 py-4 max-w-xs break-words">{item.title}</td>
                      <td className="px-4 py-4">{item.date}</td>
                      <td className="px-4 py-4">
                        <a
                          href={item.source}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          Link
                        </a>
                      </td>
                      <td className="px-4 py-4 max-w-2xl">
                        <div className="max-h-40 overflow-y-auto whitespace-pre-line border p-2 rounded bg-gray-50">
                          {item.content}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
