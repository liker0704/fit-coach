import { memo, useMemo } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { format } from 'date-fns';
import type { Day } from '@/types/models/health';
import { useContainerSize } from '@/hooks/useContainerSize';

interface EffortChartProps {
  days: Day[];
}

const EffortChartComponent = ({ days }: EffortChartProps) => {
  const [containerRef, { width }] = useContainerSize();
  const chartWidth = width > 100 ? Math.min(width - 40, 550) : 550;

  // Transform days to chart data - get AI effort score
  const data = useMemo(
    () =>
      days.map((day) => ({
        date: format(new Date(day.date), 'MM/dd'),
        score: day.effort_score || 0,
      })),
    [days]
  );

  return (
    <Card ref={containerRef}>
      <CardHeader>
        <CardTitle>AI Effort Score</CardTitle>
      </CardHeader>
      <CardContent>
        <AreaChart data={data} width={chartWidth} height={300}>
          <defs>
            <linearGradient id="effortGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.3} />
            </linearGradient>
          </defs>
          <XAxis dataKey="date" />
          <YAxis
            domain={[0, 10]}
            label={{ value: 'Effort Score', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip />
          <Legend />
          <Area
            type="monotone"
            dataKey="score"
            stroke="#8B5CF6"
            fill="url(#effortGradient)"
            strokeWidth={2}
            isAnimationActive={false}
            name="Effort"
          />
        </AreaChart>
      </CardContent>
    </Card>
  );
};

export const EffortChart = memo(EffortChartComponent);
