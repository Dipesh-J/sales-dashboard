import { useGlobalState } from '../../context/GlobalState';
import './FilterBar.css';

const exportToCSV = (data, filename) => {
    if (!data || typeof data !== 'object') return;

    // Collect all tabular arrays from dashboard data
    const sections = [];
    for (const [key, value] of Object.entries(data)) {
        if (Array.isArray(value) && value.length > 0) {
            sections.push({ name: key, rows: value });
        }
    }
    if (sections.length === 0) return;

    let csv = '';
    for (const section of sections) {
        csv += `${section.name}\n`;
        const headers = Object.keys(section.rows[0]);
        csv += headers.join(',') + '\n';
        for (const row of section.rows) {
            csv += headers.map(h => {
                const val = row[h];
                return typeof val === 'string' && val.includes(',') ? `"${val}"` : val;
            }).join(',') + '\n';
        }
        csv += '\n';
    }

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
};

const FilterBar = () => {
    const { filters, filterOptions, updateFilter, dashboardData } = useGlobalState();

    const handleChange = (key, e) => {
        updateFilter(key, e.target.value);
    };

    const handleReset = () => {
        updateFilter('dateRange', 'month');
        updateFilter('brand', 'All');
        updateFilter('category', 'All');
        updateFilter('region', 'All');
    };

    const handleExport = () => {
        if (!dashboardData) return;
        const page = window.location.pathname.includes('stores') ? 'stores_dashboard' : 'sales_dashboard';
        exportToCSV(dashboardData, page);
    };

    return (
        <div className="filter-bar">
            <div className="filter-row top-row">
                <div className="title-section">
                    <h2>Executive View</h2>
                    <span className="subtitle">Drive Sales Fundamentals Stronger, Faster & Better</span>
                </div>

                <div className="top-controls">
                    <div className="date-filter">
                        <select
                            value={filters.dateRange}
                            onChange={(e) => handleChange('dateRange', e)}
                            className="select-input date-select"
                        >
                            {filterOptions.dateRanges?.map(date => (
                                <option key={date} value={date}>{date}</option>
                            ))}
                        </select>
                    </div>

                    <button className="export-btn" onClick={handleExport} title="Export CSV">
                        ⬇ Export CSV
                    </button>

                    <div className="refresh-info">
                        <span className="icon">📅</span>
                        <span>Last Refresh: {new Date().toLocaleDateString()} {new Date().toLocaleTimeString()}</span>
                    </div>
                </div>
            </div>

            <div className="filter-row bottom-row">
                <div className="dropdowns-grid">
                    <div className="filter-group">
                        <label>Region</label>
                        <select value={filters.region} onChange={e => handleChange('region', e)} className="select-input">
                            {filterOptions.regions?.map(opt => (
                                <option key={opt} value={opt}>{opt}</option>
                            ))}
                        </select>
                    </div>

                    <div className="filter-group">
                        <label>Category</label>
                        <select value={filters.category} onChange={e => handleChange('category', e)} className="select-input">
                            {filterOptions.categories?.map(opt => (
                                <option key={opt} value={opt}>{opt}</option>
                            ))}
                        </select>
                    </div>

                    <div className="filter-group">
                        <label>Brand</label>
                        <select value={filters.brand} onChange={e => handleChange('brand', e)} className="select-input">
                            {filterOptions.brands?.map(opt => (
                                <option key={opt} value={opt}>{opt}</option>
                            ))}
                        </select>
                    </div>
                </div>

                <button className="reset-btn" onClick={handleReset}>
                    Reset
                </button>
            </div>
        </div>
    );
};

export default FilterBar;
