import { memo, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ReferenceLine,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { format } from 'date-fns';
import type { Day } from '@/types/models/health';

interface WaterChartProps {
  days: Day[];
}

const WaterChartComponent = ({ days }: WaterChartProps) => {
  // Transform days to chart data - sum all water intakes
  const data = useMemo(
    () =>
      days.map((day) => ({
        date: format(new Date(day.date), 'MM/dd'),
        liters: day.water_intakes.reduce((sum, intake) => sum + intake.amount, 0),
      })),
    [days]
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Water Intake</CardTitle>
      </CardHeader>
      <CardContent>
        <BarChart data={data} width={550} height={300}>
          <XAxis dataKey="date" />
          <YAxis label={{ value: 'Liters', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          <ReferenceLine
            y={2.5}
            stroke="red"
            strokeDasharray="3 3"
            label="Goal (2.5L)"
          />
          <Bar dataKey="liters" fill="#00C49F" name="Water (L)" isAnimationActive={false} />
        </BarChart>
      </CardContent>
    </Card>
  );
};

export const WaterChart = memo(WaterChartComponent);
