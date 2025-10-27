import { useState } from "react";

export default function Layout({ tabs, user }){
  const [current, setCurrent] = useState(tabs[0].key);

  const CurrentComp = tabs.find(t=>t.key===current).comp;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* ヘッダー */}
      <header className="bg-white shadow-md sticky top-0 z-10">
        <div className="px-4 py-3">
          <h1 className="text-lg md:text-xl font-bold text-gray-800">在庫管理システム</h1>
          <p className="text-xs md:text-sm text-gray-600">ユーザー: {user}</p>
        </div>
      </header>

      {/* ナビゲーション */}
      <nav className="bg-white shadow-sm border-b sticky top-[60px] md:top-[68px] z-10 animate-slide-in">
        {/* モバイル: 2×2グリッドレイアウト（全て表示） */}
        <div className="md:hidden grid grid-cols-2 gap-2 p-2">
          {tabs.map(t=>(
            <button
              key={t.key}
              className={`px-2 py-2.5 rounded-lg font-bold text-xs leading-tight transition-colors ${
                current===t.key
                  ? "bg-blue-600 text-white shadow-md"
                  : "bg-gray-100 text-gray-700 active:bg-gray-300"
              }`}
              onClick={()=>setCurrent(t.key)}>
              {t.label}
            </button>
          ))}
        </div>

        {/* デスクトップ: 横並びタブ */}
        <div className="hidden md:flex justify-center space-x-2 px-4 py-3">
          {tabs.map(t=>(
            <button
              key={t.key}
              className={`px-6 py-2 rounded-lg font-semibold text-base whitespace-nowrap transition-colors ${
                current===t.key
                  ? "bg-blue-600 text-white shadow-md"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
              onClick={()=>setCurrent(t.key)}>
              {t.label}
            </button>
          ))}
        </div>
      </nav>

      {/* メインコンテンツ */}
      <main className="p-4 md:p-6 pb-20">
        <CurrentComp user={user} />
      </main>

      {/* モバイル用フッター（オプション） */}
      <footer className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t py-2 px-4 text-center text-xs text-gray-500">
        在庫管理システム v1.0
      </footer>
    </div>
  );
}
