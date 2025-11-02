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
  // For now, using placeholder weight data (75kg)
  // In the future, this should extract from user profile updates
  const data = useMemo(
    () =>
      days.map((day) => ({
        date: format(new Date(day.date), 'MM/dd'),
        weight: 75, // Placeholder - extract from user profile in future
      })),
    [days]
  );

  return (
    <Card ref={containerRef}>
      <CardHeader>
        <CardTitle>Weight Trend</CardTitle>
      </CardHeader>
      <CardContent>
        <LineChart data={data} width={chartWidth} height={300}>
          <XAxis dataKey="date" />
          <YAxis domain={[60, 80]} />
          <Tooltip />
          <Legend />
          <ReferenceLine
            y={70}
            stroke="red"
            strokeDasharray="3 3"
            label="Target"
          />
          <Line
            type="monotone"
            dataKey="weight"
            stroke="#8884d8"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </CardContent>
    </Card>
  );
};

export const WeightChart = memo(WeightChartComponent);
