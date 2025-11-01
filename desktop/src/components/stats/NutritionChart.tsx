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

interface NutritionChartProps {
  days: Day[];
}

const NutritionChartComponent = ({ days }: NutritionChartProps) => {
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
    <Card>
      <CardHeader>
        <CardTitle>Daily Calories</CardTitle>
      </CardHeader>
      <CardContent>
        <LineChart data={data} width={550} height={300}>
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
