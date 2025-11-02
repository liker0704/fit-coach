import { memo, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { format } from 'date-fns';
import type { Day } from '@/types/models/health';
import { useContainerSize } from '@/hooks/useContainerSize';

interface ActivityChartProps {
  days: Day[];
}

const ActivityChartComponent = ({ days }: ActivityChartProps) => {
  const [containerRef, { width }] = useContainerSize();
  const chartWidth = width > 100 ? Math.min(width - 40, 550) : 550;

  // Transform days to chart data - sum all exercise durations
  const data = useMemo(
    () =>
      days.map((day) => ({
        date: format(new Date(day.date), 'MM/dd'),
        minutes: day.exercises.reduce(
          (sum, exercise) => sum + (exercise.duration || 0),
          0
        ),
      })),
    [days]
  );

  return (
    <Card ref={containerRef}>
      <CardHeader>
        <CardTitle>Activity Duration</CardTitle>
      </CardHeader>
      <CardContent>
        <BarChart data={data} width={chartWidth} height={300}>
          <XAxis dataKey="date" />
          <YAxis label={{ value: 'Minutes', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          <Bar dataKey="minutes" fill="#82ca9d" name="Exercise Minutes" isAnimationActive={false} />
        </BarChart>
      </CardContent>
    </Card>
  );
};

export const ActivityChart = memo(ActivityChartComponent);
