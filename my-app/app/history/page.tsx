"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import API_BASE_URL from "../../lib/api";

interface HistoryItem {
  id: string;
  request: string;
  response: string;
  timestamp: string;
  user_rating: string;
}

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const isLoggedIn = localStorage.getItem("isAdminLoggedIn");
    if (!isLoggedIn) {
      router.push("/admin");
    } else {
      fetchHistory();
    }
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/get_history`);
      const data = await response.json();
      setHistory(data.data || []);
    } catch (error) {
      console.error("Lỗi khi lấy lịch sử:", error);
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
                <Link href="/">
                  <span className="block p-2 rounded-lg hover:bg-slate-200">
                    Home
                  </span>
                </Link>
              </li>
              <li>
                <Link href="/dashboard">
                  <span className="block p-2 rounded-lg hover:bg-slate-200">
                    Dashboard
                  </span>
                </Link>
              </li>
              <li>
                <Link href="/news">
                  <span className="block p-2 rounded-lg hover:bg-slate-200">
                    News
                  </span>
                </Link>
              </li>
              <li>
                <Link href="/history">
                  <span className="block p-2 bg-slate-300 rounded-lg hover:bg-slate-200">
                    History
                  </span>
                </Link>
              </li>
            </ul>
          </nav>
        </div>
      </aside>

      {/* Main Content */}
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
          🕓 Lịch sử xác thực thông tin
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
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
                    ID
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
                    Request
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
                    Response
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
                    Feedback
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
                    Thời gian
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {history.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="text-center py-6 text-gray-500">
                      Không có dữ liệu lịch sử.
                    </td>
                  </tr>
                ) : (
                  history.map((item, index) => (
                    <tr key={index} className="text-sm text-gray-700">
                      <td className="px-4 py-4">{item.id}</td>
                      <td className="px-4 py-4 max-w-2xl">
                        <div className="max-h-40 overflow-y-auto whitespace-pre-line border p-2 rounded bg-gray-50">
                          {item.request}
                        </div>
                      </td>
                      <td className="px-4 py-4 max-w-2xl">
                        <div className="max-h-40 overflow-y-auto whitespace-pre-line border p-2 rounded bg-gray-50">
                          {item.response}
                        </div>
                      </td>
                      <td className="px-4 py-4 max-w-2xl">
                        <div className="max-h-40 overflow-y-auto whitespace-pre-line border p-2 rounded bg-gray-50">
                          {item.user_rating}
                        </div>
                      </td>
                      <td className="px-4 py-4 text-gray-600">
                        {new Date(item.timestamp).toLocaleString()}
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
