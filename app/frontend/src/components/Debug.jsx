import React, { useState } from "react";

export default function Debug({ user }) {
  const [backtestResults, setBacktestResults] = useState(null);
  const [logs, setLogs] = useState(null);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const runBacktest = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/backtest");
      const data = await res.json();
      if (data.success) {
        setBacktestResults(data.results);
      } else {
        alert("バックテストに失敗しました");
      }
    } catch (err) {
      alert("エラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  const viewLogs = async () => {
    if (!password) {
      alert("パスワードを入力してください");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/logs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password })
      });
      const data = await res.json();
      if (data.success) {
        setLogs(data.logs);
      } else {
        alert(data.error || "ログの取得に失敗しました");
      }
    } catch (err) {
      alert("エラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* バックテスト */}
      <div className="bg-white shadow rounded-lg p-4 md:p-6">
        <h2 className="text-xl md:text-2xl font-semibold mb-4">バックテスト（MAE / RMSE）</h2>
        <p className="text-sm text-gray-600 mb-4">
          過去のデータを使用してモデルの精度を検証します
        </p>

        <button
          onClick={runBacktest}
          disabled={loading}
          className="w-full md:w-auto bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold disabled:bg-gray-400">
          {loading ? "実行中..." : "バックテストを実行"}
        </button>

        {backtestResults && (
          <div className="mt-6">
            {/* モバイル表示 */}
            <div className="md:hidden space-y-4">
              {Object.entries(backtestResults).map(([bread, result]) => (
                <div key={bread} className="bg-gray-50 p-4 rounded-lg border">
                  <h3 className="font-bold text-lg mb-2">{bread}</h3>
                  {result.error ? (
                    <p className="text-gray-500">{result.error}</p>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">MAE:</span>
                        <span className="font-semibold">{result.mae}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">RMSE:</span>
                        <span className="font-semibold">{result.rmse}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">サンプル数:</span>
                        <span className="font-semibold">{result.samples}</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* デスクトップ表示 */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-200">
                  <tr>
                    <th className="p-3 text-left">パン</th>
                    <th className="p-3 text-right">MAE</th>
                    <th className="p-3 text-right">RMSE</th>
                    <th className="p-3 text-right">サンプル数</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(backtestResults).map(([bread, result]) => (
                    <tr key={bread} className="border-b">
                      <td className="p-3 font-semibold">{bread}</td>
                      {result.error ? (
                        <td colSpan="3" className="p-3 text-gray-500">{result.error}</td>
                      ) : (
                        <>
                          <td className="p-3 text-right">{result.mae}</td>
                          <td className="p-3 text-right">{result.rmse}</td>
                          <td className="p-3 text-right">{result.samples}</td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* ログ閲覧 */}
      <div className="bg-white shadow rounded-lg p-4 md:p-6">
        <h2 className="text-xl md:text-2xl font-semibold mb-4">ログ閲覧</h2>

        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="パスワード（047）"
            className="flex-1 border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={viewLogs}
            disabled={loading}
            className="w-full md:w-auto bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold disabled:bg-gray-400 whitespace-nowrap">
            {loading ? "取得中..." : "ログを表示"}
          </button>
        </div>

        {logs && (
          <div className="mt-6 overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-200">
                <tr>
                  <th className="p-2 text-left">日時</th>
                  <th className="p-2 text-left">ユーザー</th>
                  <th className="p-2 text-left">アクション</th>
                  <th className="p-2 text-left hidden md:table-cell">詳細</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, index) => (
                  <tr key={index} className="border-b">
                    <td className="p-2 text-xs">{log.created_at}</td>
                    <td className="p-2 font-semibold">{log.user}</td>
                    <td className="p-2">{log.action}</td>
                    <td className="p-2 text-xs text-gray-600 hidden md:table-cell">{log.detail || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
