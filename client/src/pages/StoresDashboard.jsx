import { useState, useEffect } from 'react';
import api from '../services/api';
import KPICard from '../components/dashboard/KPICard';
import SectionCard from '../components/dashboard/SectionCard';
import ActiveStoresTrendChart from '../components/dashboard/ActiveStoresTrendChart';
import ActiveStoresByRegionChart from '../components/dashboard/ActiveStoresByRegionChart';
import ActiveStoresByBrandChart from '../components/dashboard/ActiveStoresByBrandChart';
import DrillDownModal from '../components/dashboard/DrillDownModal';
import { useGlobalState } from '../context/GlobalState';
import './SalesDashboard.css'; // Reusing the same CSS grid layout

const sortData = (data, order) => {
    if (order === 'default' || !order) return data;
    return [...data].sort((a, b) => order === 'asc' ? a.value - b.value : b.value - a.value);
};

const StoresDashboard = () => {
    const { filters, setDashboardData } = useGlobalState();
    const [isLoading, setIsLoading] = useState(true);
    const [data, setData] = useState({
        totalActive: null,
        yoyChange: null,
        yoyPercent: null,
        storesTrend: [],
        storesByRegion: [],
        storesByBrand: []
    });

    // Sort state
    const [regionSort, setRegionSort] = useState('default');
    const [brandSort, setBrandSort] = useState('default');

    // Drill-down state
    const [drillDown, setDrillDown] = useState({ open: false, title: '', data: null, isLoading: false, columns: [] });

    useEffect(() => {
        let isMounted = true;
        const fetchData = async () => {
            setIsLoading(true);
            try {
                const query = new URLSearchParams(filters).toString();
                const [totalRes, yoyRes, trendRes, regionRes, brandRes] = await Promise.all([
                    api.get(`/api/stores/active?${query}`).catch(() => ({ data: { value: 0 } })),
                    api.get(`/api/stores/active/yoy?${query}`).catch(() => ({ data: { value: 0, percent: 0 } })),
                    api.get(`/api/stores/active/trend?${query}`).catch(() => ({ data: [] })),
                    api.get(`/api/stores/active/by-region?${query}`).catch(() => ({ data: { data: [] } })),
                    api.get(`/api/stores/active/by-brand?${query}`).catch(() => ({ data: { data: [] } }))
                ]);

                if (isMounted) {
                    const regionData = regionRes.data?.data || regionRes.data || [];
                    const brandData = brandRes.data?.data || brandRes.data || [];

                    const newData = {
                        totalActive: totalRes.data?.value || 0,
                        yoyChange: yoyRes.data?.value || 0,
                        yoyPercent: yoyRes.data?.percent || 0,
                        storesTrend: trendRes.data || [],
                        storesByRegion: regionData,
                        storesByBrand: brandData
                    };
                    setData(newData);
                    setDashboardData({
                        storesByRegion: newData.storesByRegion,
                        storesTrend: newData.storesTrend
                    });
                }
            } catch (error) {
                console.error("Dashboard data fetch failed", error);
            } finally {
                if (isMounted) setIsLoading(false);
            }
        };

        fetchData();
        return () => { isMounted = false; };
    }, [filters, setDashboardData]);

    const handleRegionDrillDown = async (entry) => {
        setDrillDown({ open: true, title: `Active Stores in "${entry.region}" by Brand`, data: null, isLoading: true, columns: [
            { key: 'brand', label: 'Brand' },
            { key: 'value', label: 'Active Stores' }
        ]});
        try {
            const query = new URLSearchParams({ ...filters, region: entry.region }).toString();
            const res = await api.get(`/api/stores/active/by-brand?${query}`);
            const items = res.data?.data || res.data || [];
            setDrillDown(prev => ({ ...prev, data: items, isLoading: false }));
        } catch {
            setDrillDown(prev => ({ ...prev, data: [], isLoading: false }));
        }
    };

    const handleBrandDrillDown = async (entry) => {
        setDrillDown({ open: true, title: `Active Stores for "${entry.brand}" by Region`, data: null, isLoading: true, columns: [
            { key: 'region', label: 'Region' },
            { key: 'value', label: 'Active Stores' }
        ]});
        try {
            const query = new URLSearchParams({ ...filters, brand: entry.brand }).toString();
            const res = await api.get(`/api/stores/active/by-region?${query}`);
            const items = res.data?.data || res.data || [];
            setDrillDown(prev => ({ ...prev, data: items, isLoading: false }));
        } catch {
            setDrillDown(prev => ({ ...prev, data: [], isLoading: false }));
        }
    };

    return (
        <div className="dashboard-container">
            <div className="kpi-grid">
                <SectionCard title="Coverage KPIs" color="var(--color-coverage-header)">
                    <KPICard title="Total Active Stores" value={data.totalActive} isLoading={isLoading} />
                    <KPICard title="YoY Change" value={isLoading ? '-' : data.yoyChange} trendValue={data.yoyChange} percent={data.yoyPercent} isLoading={isLoading} />
                </SectionCard>
            </div>

            <div className="chart-grid">
                <div style={{ gridColumn: 'span 2' }}>
                    <ActiveStoresTrendChart data={data.storesTrend} title="Active Stores Trend" isLoading={isLoading} />
                </div>
                <ActiveStoresByRegionChart
                    data={sortData(data.storesByRegion, regionSort)}
                    title="Active Stores by Region"
                    isLoading={isLoading}
                    sortable
                    sortOrder={regionSort}
                    onSortChange={setRegionSort}
                    onBarClick={handleRegionDrillDown}
                />
                <ActiveStoresByBrandChart
                    data={sortData(data.storesByBrand, brandSort)}
                    title="Active Stores by Brand"
                    isLoading={isLoading}
                    sortable
                    sortOrder={brandSort}
                    onSortChange={setBrandSort}
                    onBarClick={handleBrandDrillDown}
                />
            </div>

            <DrillDownModal
                open={drillDown.open}
                onClose={() => setDrillDown(prev => ({ ...prev, open: false }))}
                title={drillDown.title}
                data={drillDown.data}
                isLoading={drillDown.isLoading}
                columns={drillDown.columns}
            />
        </div>
    );
};

export default StoresDashboard;
