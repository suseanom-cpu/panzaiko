import { useEffect, useState } from "react";
import HolidayBanner from "./HolidayBanner";
import WeatherBanner from "./WeatherBanner";

export default function Dashboard({ user }) {
  const [data, setData] = useState(null);

  useEffect(()=>{
    fetch("/api/dashboard")
      .then(res=>res.json())
      .then(j=>setData(j));
  }, []);

  if(!data) return <p className="text-center py-8">読み込み中…</p>;

  return (
    <div className="max-w-6xl mx-auto">
      <HolidayBanner isHoliday={data.holidayTomorrowChina} events={data.events || []} />
      <WeatherBanner weather={data.weather} />

      <h2 className="text-xl md:text-2xl font-semibold mb-4">注文推奨一覧</h2>

      {/* モバイル表示: カードレイアウト */}
      <div className="md:hidden space-y-4">
        {Object.entries(data.recommendations).map(([bread, rec])=>(
          <div key={bread} className="bg-white shadow rounded-lg p-4 animate-fade-in">
            <h3 className="text-lg font-bold mb-3 text-blue-600">{bread}</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-gray-600">予測:</span>
                <span className="ml-2 font-semibold">{rec.forecast}</span>
              </div>
              <div>
                <span className="text-gray-600">σ:</span>
                <span className="ml-2 font-semibold">{rec.sigma}</span>
              </div>
              <div>
                <span className="text-gray-600">目標在庫:</span>
                <span className="ml-2 font-semibold">{rec.target}</span>
              </div>
              <div>
                <span className="text-gray-600">現余り:</span>
                <span className="ml-2 font-semibold">{rec.leftover}</span>
              </div>
              <div className="col-span-2 mt-2 pt-2 border-t">
                <span className="text-gray-600">注文量:</span>
                <span className="ml-2 text-xl font-bold text-green-600">{rec.order}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* デスクトップ表示: テーブルレイアウト */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full bg-white shadow rounded-lg overflow-hidden animate-fade-in">
          <thead className="bg-gray-200">
            <tr>
              <th className="p-3 text-left">パン</th>
              <th className="p-3 text-right">予測</th>
              <th className="p-3 text-right">σ</th>
              <th className="p-3 text-right">目標在庫</th>
              <th className="p-3 text-right">現余り</th>
              <th className="p-3 text-right">注文量</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(data.recommendations).map(([bread, rec])=>(
              <tr key={bread} className="border-b hover:bg-gray-50">
                <td className="p-3 font-semibold">{bread}</td>
                <td className="p-3 text-right">{rec.forecast}</td>
                <td className="p-3 text-right">{rec.sigma}</td>
                <td className="p-3 text-right">{rec.target}</td>
                <td className="p-3 text-right">{rec.leftover}</td>
                <td className="p-3 text-right font-bold text-green-600 text-lg">{rec.order}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6">
        <button
          className="w-full md:w-auto bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-semibold text-lg shadow-lg"
          onClick={()=>window.history.pushState({}, "", "#input")}>
          データ入力へ移動
        </button>
      </div>
    </div>
  );
}
