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

interface SleepChartProps {
  days: Day[];
}

const SleepChartComponent = ({ days }: SleepChartProps) => {
  // Transform days to chart data - get sleep duration
  const data = useMemo(
    () =>
      days.map((day) => ({
        date: format(new Date(day.date), 'MM/dd'),
        hours: day.sleep_records[0]?.duration || 0,
      })),
    [days]
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sleep Duration</CardTitle>
      </CardHeader>
      <CardContent>
        <LineChart data={data} width={550} height={300}>
          <XAxis dataKey="date" />
          <YAxis
            domain={[0, 12]}
            label={{ value: 'Hours', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip />
          <Legend />
          <ReferenceLine
            y={7}
            stroke="green"
            strokeDasharray="3 3"
            label="Baseline (7h)"
          />
          <Line
            type="monotone"
            dataKey="hours"
            stroke="#8B5CF6"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
            name="Sleep (hours)"
          />
        </LineChart>
      </CardContent>
    </Card>
  );
};

export const SleepChart = memo(SleepChartComponent);
