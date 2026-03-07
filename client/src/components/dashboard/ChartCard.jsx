import './ChartCard.css';

const sortIcons = { default: '⇅', asc: '↑', desc: '↓' };

const ChartCard = ({ title, isLoading, children, error, sortable, sortOrder, onSortChange }) => {
    const handleSort = () => {
        const next = sortOrder === 'default' ? 'desc' : sortOrder === 'desc' ? 'asc' : 'default';
        onSortChange(next);
    };

    return (
        <div className="chart-card">
            {title && (
                <div className="chart-card-header">
                    <span>{title}</span>
                    {sortable && (
                        <button className="sort-btn" onClick={handleSort} title={`Sort: ${sortOrder}`}>
                            {sortIcons[sortOrder || 'default']}
                        </button>
                    )}
                </div>
            )}

            <div className="chart-card-body">
                {isLoading ? (
                    <div className="skeleton-loader chart-skeleton" />
                ) : error ? (
                    <div className="chart-error">
                        Failed to load data
                    </div>
                ) : (
                    children
                )}
            </div>
        </div>
    );
};

export default ChartCard;
