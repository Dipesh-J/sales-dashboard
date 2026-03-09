import { useState, useEffect } from 'react';
import api from '../services/api';
import KPICard from '../components/dashboard/KPICard';
import SectionCard from '../components/dashboard/SectionCard';
import SalesTrendChart from '../components/dashboard/SalesTrendChart';
import SalesByBrandChart from '../components/dashboard/SalesByBrandChart';
import SalesByRegionChart from '../components/dashboard/SalesByRegionChart';
import SalesByCategoryChart from '../components/dashboard/SalesByCategoryChart';
import DrillDownModal from '../components/dashboard/DrillDownModal';
import { useGlobalState } from '../context/GlobalState';
import './SalesDashboard.css';

const sortData = (data, order) => {
    if (order === 'default' || !order) return data;
    return [...data].sort((a, b) => order === 'asc' ? a.value - b.value : b.value - a.value);
};

const SalesDashboard = () => {
    const { filters, setDashboardData } = useGlobalState();
    const [isLoading, setIsLoading] = useState(true);
    const [data, setData] = useState({
        totalSales: null,
        yoyGrowth: null,
        topBrand: null,
        salesTrend: [],
        salesByBrand: [],
        salesByRegion: [],
        salesByCategory: []
    });

    // Sort state per chart
    const [brandSort, setBrandSort] = useState('default');
    const [regionSort, setRegionSort] = useState('default');
    const [categorySort, setCategorySort] = useState('default');

    // Drill-down state
    const [drillDown, setDrillDown] = useState({ open: false, title: '', data: null, isLoading: false, columns: [] });

    useEffect(() => {
        let isMounted = true;
        const fetchData = async () => {
            setIsLoading(true);
            try {
                const query = new URLSearchParams(filters).toString();
                const [totalRes, yoyRes, trendRes, brandRes, regionRes, categoryRes] = await Promise.all([
                    api.get(`/api/sales/total?${query}`).catch(() => ({ data: { value: 0 } })),
                    api.get(`/api/sales/yoy?${query}`).catch(() => ({ data: { value: 0, percent: 0 } })),
                    api.get(`/api/sales/trend?${query}`).catch(() => ({ data: [] })),
                    api.get(`/api/sales/by-brand?${query}`).catch(() => ({ data: { data: [] } })),
                    api.get(`/api/sales/by-region?${query}`).catch(() => ({ data: { data: [] } })),
                    api.get(`/api/sales/by-category?${query}`).catch(() => ({ data: { data: [] } }))
                ]);

                if (isMounted) {
                    const brandData = brandRes.data?.data || brandRes.data || [];
                    const regionData = regionRes.data?.data || regionRes.data || [];
                    const categoryData = categoryRes.data?.data || categoryRes.data || [];

                    const newData = {
                        totalSales: totalRes.data?.value ? `$${(totalRes.data.value / 1000000).toFixed(1)}M` : '$0M',
                        yoyGrowth: yoyRes.data?.percent || 0,
                        topBrand: brandData[0]?.brand || '-',
                        salesTrend: trendRes.data || [],
                        salesByBrand: brandData,
                        salesByRegion: regionData,
                        salesByCategory: categoryData
                    };
                    setData(newData);
                    setDashboardData({
                        salesByBrand: newData.salesByBrand,
                        salesByRegion: newData.salesByRegion,
                        salesTrend: newData.salesTrend
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

    const handleBrandDrillDown = async (entry) => {
        setDrillDown({ open: true, title: `Products under "${entry.brand}"`, data: null, isLoading: true, columns: [
            { key: 'name', label: 'Product' },
            { key: 'value', label: 'Sales', format: v => `$${Number(v).toLocaleString()}` }
        ]});
        try {
            const query = new URLSearchParams({ ...filters, brand: entry.brand }).toString();
            const res = await api.get(`/api/sales/top-products?n=20&${query}`);
            const items = res.data?.data || res.data || [];
            setDrillDown(prev => ({ ...prev, data: items, isLoading: false }));
        } catch {
            setDrillDown(prev => ({ ...prev, data: [], isLoading: false }));
        }
    };

    const handleRegionDrillDown = async (entry) => {
        setDrillDown({ open: true, title: `Sales in "${entry.region}" by Brand`, data: null, isLoading: true, columns: [
            { key: 'brand', label: 'Brand' },
            { key: 'value', label: 'Sales', format: v => `$${Number(v).toLocaleString()}` }
        ]});
        try {
            const query = new URLSearchParams({ ...filters, region: entry.region }).toString();
            const res = await api.get(`/api/sales/by-brand?${query}`);
            const items = res.data?.data || res.data || [];
            setDrillDown(prev => ({ ...prev, data: items, isLoading: false }));
        } catch {
            setDrillDown(prev => ({ ...prev, data: [], isLoading: false }));
        }
    };

    const handleCategoryDrillDown = async (entry) => {
        setDrillDown({ open: true, title: `Top Products in "${entry.name}"`, data: null, isLoading: true, columns: [
            { key: 'name', label: 'Product' },
            { key: 'value', label: 'Sales', format: v => `$${Number(v).toLocaleString()}` }
        ]});
        try {
            const query = new URLSearchParams({ ...filters, category: entry.name }).toString();
            const res = await api.get(`/api/sales/top-products?n=20&${query}`);
            const items = res.data?.data || res.data || [];
            setDrillDown(prev => ({ ...prev, data: items, isLoading: false }));
        } catch {
            setDrillDown(prev => ({ ...prev, data: [], isLoading: false }));
        }
    };

    return (
        <div className="dashboard-container">
            <div className="kpi-grid">
                <SectionCard title="Sales KPIs" color="var(--color-sales-header)">
                    <KPICard title="Total Sales" value={data.totalSales} isLoading={isLoading} />
                    <KPICard title="YoY Growth %" value={isLoading ? '-' : `${data.yoyGrowth}%`} trendValue={data.yoyGrowth} percent={data.yoyGrowth} isLoading={isLoading} />
                    <KPICard title="Top Brand" value={data.topBrand} isLoading={isLoading} />
                </SectionCard>
            </div>

            <div className="chart-grid">
                <SalesTrendChart data={data.salesTrend} title="Sales Trend over Time" isLoading={isLoading} />
                <SalesByBrandChart
                    data={sortData(data.salesByBrand, brandSort)}
                    title="Sales by Brand"
                    isLoading={isLoading}
                    sortable
                    sortOrder={brandSort}
                    onSortChange={setBrandSort}
                    onBarClick={handleBrandDrillDown}
                />
                <SalesByRegionChart
                    data={sortData(data.salesByRegion, regionSort)}
                    title="Sales by Region"
                    isLoading={isLoading}
                    sortable
                    sortOrder={regionSort}
                    onSortChange={setRegionSort}
                    onBarClick={handleRegionDrillDown}
                />
                <SalesByCategoryChart
                    data={sortData(data.salesByCategory, categorySort)}
                    title="Sales by Category"
                    isLoading={isLoading}
                    sortable
                    sortOrder={categorySort}
                    onSortChange={setCategorySort}
                    onBarClick={handleCategoryDrillDown}
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

export default SalesDashboard;
