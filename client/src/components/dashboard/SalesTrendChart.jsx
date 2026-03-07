import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import ChartCard from './ChartCard';

const SalesTrendChart = ({ data, title, isLoading, error }) => {
    return (
        <ChartCard title={title} isLoading={isLoading} error={error}>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <defs>
                        <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--color-magenta)" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="var(--color-magenta)" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" />
                    <XAxis
                        dataKey="date"
                        tick={{ fill: 'var(--color-text-gray)', fontSize: 12 }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <YAxis
                        tickFormatter={(value) => `$${value / 1000}k`}
                        tick={{ fill: 'var(--color-text-gray)', fontSize: 12 }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <Tooltip
                        formatter={(value) => [`$${value.toLocaleString()}`, 'Sales']}
                        contentStyle={{ borderRadius: '4px', border: '1px solid var(--color-border)' }}
                    />
                    <Area type="monotone" dataKey="value" stroke="var(--color-magenta)" fillOpacity={1} fill="url(#colorSales)" />
                </AreaChart>
            </ResponsiveContainer>
        </ChartCard>
    );
};

export default SalesTrendChart;
