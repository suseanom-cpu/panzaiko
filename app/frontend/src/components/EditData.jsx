import { useEffect, useState } from "react";

const BREADS = ["細パン", "太パン", "サンドパン", "バゲット"];

export default function EditData({ user }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    loadRecords();
  }, []);

  const loadRecords = async () => {
    try {
      const res = await fetch("/api/records?days=7");
      const data = await res.json();
      setRecords(data.records || []);
    } catch(err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (record) => {
    setEditingId(record.id);
    setEditForm({ sold: record.sold, leftover: record.leftover });
  };

  const saveEdit = async (id) => {
    try {
      await fetch(`/api/records/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(editForm)
      });
      setEditingId(null);
      loadRecords();
      alert("更新しました");
    } catch(err) {
      alert("エラーが発生しました");
    }
  };

  const deleteRecord = async (id) => {
    if (!confirm("本当に削除しますか?")) return;
    try {
      await fetch(`/api/records/${id}`, { method: "DELETE" });
      loadRecords();
      alert("削除しました");
    } catch(err) {
      alert("エラーが発生しました");
    }
  };

  if (loading) return <p className="text-center py-8">読み込み中...</p>;

  // 日付ごとにグループ化
  const groupedRecords = records.reduce((acc, rec) => {
    if (!acc[rec.day]) acc[rec.day] = [];
    acc[rec.day].push(rec);
    return acc;
  }, {});

  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-xl md:text-2xl font-semibold mb-4">データ修正</h2>
      <p className="text-gray-600 mb-6">過去7日間のデータを編集できます</p>

      {Object.keys(groupedRecords).length === 0 ? (
        <p className="text-center text-gray-500">データがありません</p>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedRecords).map(([day, dayRecords]) => (
            <div key={day} className="bg-white shadow rounded-lg p-4 md:p-6">
              <h3 className="font-bold text-lg mb-4 text-gray-800">{day}</h3>

              {/* モバイル表示 */}
              <div className="md:hidden space-y-4">
                {dayRecords.map(rec => (
                  <div key={rec.id} className="border rounded-lg p-3 bg-gray-50">
                    <div className="font-semibold text-blue-600 mb-2">{rec.bread}</div>
                    {editingId === rec.id ? (
                      <div className="space-y-2">
                        <div>
                          <label className="text-xs text-gray-600">売れた数</label>
                          <input
                            type="number"
                            min="0"
                            value={editForm.sold}
                            onChange={e => setEditForm({...editForm, sold: e.target.value})}
                            className="w-full border rounded p-2 mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-600">余り数</label>
                          <input
                            type="number"
                            min="0"
                            value={editForm.leftover}
                            onChange={e => setEditForm({...editForm, leftover: e.target.value})}
                            className="w-full border rounded p-2 mt-1"
                          />
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => saveEdit(rec.id)}
                            className="flex-1 bg-green-600 text-white py-2 rounded text-sm">
                            保存
                          </button>
                          <button
                            onClick={() => setEditingId(null)}
                            className="flex-1 bg-gray-400 text-white py-2 rounded text-sm">
                            キャンセル
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div className="text-sm mb-2">
                          <span className="text-gray-600">売れた: </span>
                          <span className="font-semibold">{rec.sold}</span>
                          <span className="text-gray-600 ml-3">余り: </span>
                          <span className="font-semibold">{rec.leftover}</span>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => startEdit(rec)}
                            className="flex-1 bg-blue-600 text-white py-2 rounded text-sm">
                            編集
                          </button>
                          <button
                            onClick={() => deleteRecord(rec.id)}
                            className="flex-1 bg-red-600 text-white py-2 rounded text-sm">
                            削除
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* デスクトップ表示 */}
              <div className="hidden md:block overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="p-2 text-left">パン</th>
                      <th className="p-2 text-right">売れた数</th>
                      <th className="p-2 text-right">余り数</th>
                      <th className="p-2 text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dayRecords.map(rec => (
                      <tr key={rec.id} className="border-b">
                        <td className="p-2 font-semibold">{rec.bread}</td>
                        {editingId === rec.id ? (
                          <>
                            <td className="p-2">
                              <input
                                type="number"
                                min="0"
                                value={editForm.sold}
                                onChange={e => setEditForm({...editForm, sold: e.target.value})}
                                className="w-20 border rounded p-1 text-right"
                              />
                            </td>
                            <td className="p-2">
                              <input
                                type="number"
                                min="0"
                                value={editForm.leftover}
                                onChange={e => setEditForm({...editForm, leftover: e.target.value})}
                                className="w-20 border rounded p-1 text-right"
                              />
                            </td>
                            <td className="p-2 text-center space-x-2">
                              <button
                                onClick={() => saveEdit(rec.id)}
                                className="bg-green-600 text-white px-3 py-1 rounded text-sm">
                                保存
                              </button>
                              <button
                                onClick={() => setEditingId(null)}
                                className="bg-gray-400 text-white px-3 py-1 rounded text-sm">
                                キャンセル
                              </button>
                            </td>
                          </>
                        ) : (
                          <>
                            <td className="p-2 text-right">{rec.sold}</td>
                            <td className="p-2 text-right">{rec.leftover}</td>
                            <td className="p-2 text-center space-x-2">
                              <button
                                onClick={() => startEdit(rec)}
                                className="bg-blue-600 text-white px-3 py-1 rounded text-sm">
                                編集
                              </button>
                              <button
                                onClick={() => deleteRecord(rec.id)}
                                className="bg-red-600 text-white px-3 py-1 rounded text-sm">
                                削除
                              </button>
                            </td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
