export default function WeatherBanner({ weather }) {
  if(!weather) return null;
  const cond = weather.current.condition.text;
  const temp = weather.current.temp_c;
  return (
    <div className="bg-blue-50 border-l-4 border-blue-400 text-blue-800 p-4 mb-4 animate-slide-down">
      <p>神戸市中央区の予報： 気温 {temp}°C / 状況：{cond}</p>
    </div>
  );
}
