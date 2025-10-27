import { useState } from "react";
import Layout from "./components/Layout";
import Dashboard from "./components/Dashboard";
import InputData from "./components/InputData";
import EditData from "./components/EditData";
import Debug from "./components/Debug";

const tabs = [
  { key: "dashboard", label: "ダッシュボード", comp: Dashboard },
  { key: "input", label: "データ入力", comp: InputData },
  { key: "edit", label: "データ修正", comp: EditData },
  { key: "debug", label: "デバッグ", comp: Debug },
];

export default function App(){
  const [user, setUser] = useState(null);

  const login = async (name)=>{
    const res = await fetch("/api/login", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({username: name})
    });
    const j = await res.json();
    if(j.success) setUser(name);
    else alert(j.error);
  };

  if(!user){
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 px-4">
        <div className="w-full max-w-md p-6 md:p-8 bg-white shadow-xl rounded-2xl animate-fade-in">
          <div className="text-center mb-6">
            <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mb-2">在庫管理システム</h1>
            <p className="text-sm text-gray-600">ログインしてください</p>
          </div>

          <form onSubmit={(e)=>{
            e.preventDefault();
            const name = document.getElementById("nameInput").value;
            if(name.trim()) login(name);
          }}>
            <div className="mb-4">
              <label htmlFor="nameInput" className="block text-sm font-medium text-gray-700 mb-2">
                ユーザー名
              </label>
              <input
                type="text"
                id="nameInput"
                placeholder="名前を入力"
                className="w-full border border-gray-300 rounded-lg p-3 text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                autoFocus
                required
              />
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold text-lg hover:bg-blue-700 transition-colors shadow-lg">
              ログイン
            </button>
          </form>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-xs text-gray-700 mb-2 font-semibold">テストユーザー:</p>
            <p className="text-sm text-blue-600 font-mono">テストユーザー</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Layout tabs={tabs} user={user} />
  );
}
