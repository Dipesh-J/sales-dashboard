import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import ChartCard from './ChartCard';

const ActiveStoresTrendChart = ({ data, title, isLoading, error }) => {
    return (
        <ChartCard title={title} isLoading={isLoading} error={error}>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" />
                    <XAxis
                        dataKey="date"
                        tick={{ fill: 'var(--color-text-gray)', fontSize: 12 }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <YAxis
                        tick={{ fill: 'var(--color-text-gray)', fontSize: 12 }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <Tooltip
                        contentStyle={{ borderRadius: '4px', border: '1px solid var(--color-border)' }}
                    />
                    <Line type="monotone" dataKey="value" stroke="var(--color-coverage-header)" strokeWidth={3} dot={{ r: 4, fill: 'var(--color-coverage-header)' }} activeDot={{ r: 6 }} />
                </LineChart>
            </ResponsiveContainer>
        </ChartCard>
    );
};

export default ActiveStoresTrendChart;
