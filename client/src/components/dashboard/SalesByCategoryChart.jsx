import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import ChartCard from './ChartCard';

const SalesByCategoryChart = ({ data, title, isLoading, error, onBarClick, sortable, sortOrder, onSortChange }) => {
    const handleClick = (entry) => {
        if (onBarClick && entry) onBarClick(entry);
    };

    return (
        <ChartCard title={title} isLoading={isLoading} error={error} sortable={sortable} sortOrder={sortOrder} onSortChange={onSortChange}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" />
                    <XAxis
                        dataKey="name"
                        tick={{ fill: 'var(--color-text-gray)', fontSize: 12 }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <YAxis
                        tickFormatter={(val) => `$${val / 1000}k`}
                        tick={{ fill: 'var(--color-text-gray)', fontSize: 12 }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <Tooltip
                        formatter={(val) => [`$${val.toLocaleString()}`, 'Sales']}
                        cursor={{ fill: 'rgba(0,0,0,0.05)' }}
                        contentStyle={{ borderRadius: '4px', border: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-card)' }}
                    />
                    <Bar
                        dataKey="value"
                        fill="var(--color-sales-header)"
                        radius={[4, 4, 0, 0]}
                        cursor="pointer"
                        onClick={(_, index) => handleClick(data[index])}
                    />
                </BarChart>
            </ResponsiveContainer>
        </ChartCard>
    );
};

export default SalesByCategoryChart;
