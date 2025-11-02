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

interface NutritionChartProps {
  days: Day[];
}

const NutritionChartComponent = ({ days }: NutritionChartProps) => {
  const [containerRef, { width }] = useContainerSize();
  const chartWidth = width > 100 ? Math.min(width - 40, 550) : 550;

  // Transform days to chart data - sum all meal calories
  const data = useMemo(
    () =>
      days.map((day) => ({
        date: format(new Date(day.date), 'MM/dd'),
        calories: day.meals.reduce((sum, meal) => sum + (meal.calories || 0), 0),
      })),
    [days]
  );

  return (
    <Card ref={containerRef}>
      <CardHeader>
        <CardTitle>Daily Calories</CardTitle>
      </CardHeader>
      <CardContent>
        <LineChart data={data} width={chartWidth} height={300}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <ReferenceLine
            y={2000}
            stroke="red"
            strokeDasharray="3 3"
            label="Goal (2000 kcal)"
          />
          <Line
            type="monotone"
            dataKey="calories"
            stroke="#ffc658"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
            name="Calories"
          />
        </LineChart>
      </CardContent>
    </Card>
  );
};

export const NutritionChart = memo(NutritionChartComponent);
