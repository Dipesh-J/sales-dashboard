import './KPICard.css';

const KPICard = ({ title, value, subValue, trendValue, percent, isLoading }) => {
    const isPositiveTrend = String(trendValue || '').startsWith('+') || typeof trendValue === 'number' && trendValue >= 0;
    const isPositivePercent = String(percent || '').startsWith('+') || typeof percent === 'number' && percent >= 0;

    return (
        <div className="kpi-card">
            <div className="kpi-title">{title}</div>

            {isLoading ? (
                <div className="skeleton-loader h-32 w-full mt-2" />
            ) : (
                <div className="kpi-body">
                    <div className="kpi-main-val">
                        {value !== undefined ? value : '-'}
                    </div>

                    <div className="kpi-footer">
                        {subValue !== undefined && (
                            <span className="kpi-sub-val">{subValue}</span>
                        )}
                        {trendValue !== undefined && (
                            <span className={`kpi-trend ${isPositiveTrend ? 'positive' : 'negative'}`}>
                                {trendValue > 0 && typeof trendValue === 'number' ? `+${trendValue}` : trendValue}
                            </span>
                        )}
                        {percent !== undefined && (
                            <span className={`kpi-percent ${isPositivePercent ? 'positive' : 'negative'}`}>
                                {percent > 0 && typeof percent === 'number' ? `+${percent}%` : percent}
                            </span>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default KPICard;
