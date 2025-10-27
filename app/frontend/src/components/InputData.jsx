import { useEffect, useState } from "react";

const BREADS = ["細パン", "太パン", "サンドパン", "バゲット"];

export default function InputData({ user }) {
  const [forecastData, setForecastData] = useState(null);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(()=>{
    fetch("/api/dashboard").then(r=>r.json()).then(j=>setForecastData(j.recommendations));
  }, []);

  const handleChange = (bread, field, val)=>{
    setForm({...form, [bread]: {...(form[bread]||{}), [field]: val}});
  };

  const submit = async ()=>{
    setLoading(true);
    try {
      await fetch("/api/input", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify(form)
      });
      alert("入力完了しました!");
      window.location.reload();
    } catch(err) {
      alert("エラーが発生しました");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-xl md:text-2xl font-semibold mb-2">今日の販売入力</h2>
      <p className="text-sm text-gray-600 mb-4">
        今日買ったパンの個数と、余った個数を入力してください
      </p>

      {/* 予測データの表示 */}
      {forecastData && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">📊 本日の注文推奨</h3>

          {/* モバイル表示 */}
          <div className="md:hidden grid grid-cols-2 gap-3">
            {BREADS.map(b=>{
              const rec = forecastData[b];
              return (
                <div key={b} className="bg-gradient-to-br from-blue-50 to-blue-100 p-3 rounded-lg border border-blue-200">
                  <div className="font-bold text-base text-blue-900 mb-1">{b}</div>
                  <div className="text-xs text-gray-700">
                    <span className="font-semibold text-green-700">推奨: {rec.order}個</span>
                  </div>
                  <div className="text-xs text-gray-600 mt-1">予測: {rec.forecast}個</div>
                </div>
              );
            })}
          </div>

          {/* デスクトップ表示 */}
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full bg-white shadow rounded-lg">
              <thead className="bg-gray-200">
                <tr>
                  <th className="p-3 text-left">パン</th>
                  <th className="p-3 text-right">予測</th>
                  <th className="p-3 text-right">注文推奨</th>
                </tr>
              </thead>
              <tbody>
                {BREADS.map(b=>{
                  const rec = forecastData[b];
                  return (
                    <tr key={b} className="border-b">
                      <td className="p-3 font-semibold">{b}</td>
                      <td className="p-3 text-right">{rec.forecast}</td>
                      <td className="p-3 text-right font-bold text-green-600">{rec.order}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 入力フォーム */}
      <h3 className="text-sm font-semibold text-gray-700 mb-3">✏️ 販売データ入力</h3>
      <form onSubmit={(e)=>{e.preventDefault();submit();}} className="space-y-4">
        {BREADS.map((b, index)=>(
          <div key={b} className="bg-white shadow-lg rounded-lg p-4 border-l-4 border-blue-500">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-lg text-gray-800">{b}</h3>
              {forecastData && (
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full font-semibold">
                  推奨: {forecastData[b].order}個
                </span>
              )}
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  🛒 買った個数（仕入れた数）
                </label>
                <input
                  type="number"
                  min="0"
                  placeholder="例: 25"
                  className="w-full border-2 border-gray-300 rounded-lg p-3 text-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  onChange={e=>handleChange(b, "purchased", e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  📦 余った個数（売れ残り）
                </label>
                <input
                  type="number"
                  min="0"
                  placeholder="例: 3"
                  className="w-full border-2 border-gray-300 rounded-lg p-3 text-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  onChange={e=>handleChange(b, "leftover", e.target.value)}
                  required
                />
              </div>
            </div>
          </div>
        ))}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white px-6 py-4 rounded-lg hover:bg-blue-700 font-semibold text-lg shadow-lg disabled:bg-gray-400 disabled:cursor-not-allowed">
          {loading ? "送信中..." : "送信"}
        </button>
      </form>

      <div className="mt-6 text-center">
        <button
          className="text-blue-600 underline hover:text-blue-800"
          onClick={()=>window.history.pushState({}, "", "#")}>
          ダッシュボードに戻る
        </button>
      </div>
    </div>
  );
}
