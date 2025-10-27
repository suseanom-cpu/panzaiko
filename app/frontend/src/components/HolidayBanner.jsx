export default function HolidayBanner({ isHoliday, events }) {
  if(!events || events.length === 0) return null;

  // 今日から7日以内のイベントを表示
  const upcomingEvents = events.filter(e => e.days_until <= 7);

  if(upcomingEvents.length === 0) return null;

  return (
    <div className="mb-4 space-y-3">
      {upcomingEvents.map((event, index) => {
        const isToday = event.days_until === 0;
        const isTomorrow = event.days_until === 1;
        const daysText = isToday ? "今日" : isTomorrow ? "明日" : `${event.days_until}日後`;

        const bgColor = event.impact === "very_high" ? "bg-red-100 border-red-500" :
                       event.impact === "high" ? "bg-orange-100 border-orange-500" :
                       "bg-yellow-100 border-yellow-500";

        const textColor = event.impact === "very_high" ? "text-red-800" :
                         event.impact === "high" ? "text-orange-800" :
                         "text-yellow-800";

        const impactText = event.impact === "very_high" ? "🔥 来客数大幅増加予想" :
                          event.impact === "high" ? "⚠️ 来客数増加予想" :
                          "ℹ️ 来客数やや増加";

        return (
          <div key={index} className={`${bgColor} border-l-4 ${textColor} p-3 md:p-4 rounded-r-lg shadow-md animate-fade-in`}>
            <div className="flex items-start justify-between flex-wrap gap-2">
              <div className="flex-1 min-w-0">
                <p className="font-bold text-base md:text-lg mb-1">🇨🇳 {event.name}</p>
                <p className="text-xs md:text-sm">{impactText}</p>
              </div>
              <div className="text-right shrink-0">
                <span className="inline-block bg-white bg-opacity-70 px-2 md:px-3 py-1 rounded-full text-xs md:text-sm font-semibold">
                  {daysText}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
