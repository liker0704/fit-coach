import { memo, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ReferenceLine,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { format } from 'date-fns';
import type { Day } from '@/types/models/health';
import { useContainerSize } from '@/hooks/useContainerSize';

interface WeightChartProps {
  days: Day[];
}

const WeightChartComponent = ({ days }: WeightChartProps) => {
  const [containerRef, { width }] = useContainerSize();
  const chartWidth = width > 100 ? Math.min(width - 40, 550) : 550;

  // Transform days to chart data
  const data = useMemo(
    () =>
      days
        .filter((day) => day.weight != null) // Only include days with weight recorded
        .map((day) => ({
          date: format(new Date(day.date), 'MM/dd'),
          weight: Number(day.weight),
        })),
    [days]
  );

  // Calculate dynamic Y-axis domain based on actual weight data
  const weights = data.map((d) => d.weight);
  const minWeight = weights.length > 0 ? Math.min(...weights) : 60;
  const maxWeight = weights.length > 0 ? Math.max(...weights) : 80;
  const padding = 5; // Add 5kg padding
  const yDomain = [Math.max(0, minWeight - padding), maxWeight + padding];

  return (
    <Card ref={containerRef}>
      <CardHeader>
        <CardTitle>Weight Trend</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <div className="flex items-center justify-center h-[300px] text-muted-foreground">
            <p>No weight data recorded yet. Add weight in the daily view to see your trend.</p>
          </div>
        ) : (
          <LineChart data={data} width={chartWidth} height={300}>
            <XAxis dataKey="date" />
            <YAxis domain={yDomain} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="weight"
              stroke="#8884d8"
              strokeWidth={2}
              dot={{ fill: '#8884d8', r: 4 }}
              isAnimationActive={false}
            />
          </LineChart>
        )}
      </CardContent>
    </Card>
  );
};

export const WeightChart = memo(WeightChartComponent);
