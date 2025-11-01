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

interface MoodChartProps {
  days: Day[];
}

const MoodChartComponent = ({ days }: MoodChartProps) => {
  // Transform days to chart data - get mood level
  const data = useMemo(
    () =>
      days.map((day) => ({
        date: format(new Date(day.date), 'MM/dd'),
        mood: day.mood_records[0]?.mood_level || 0,
      })),
    [days]
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mood Levels</CardTitle>
      </CardHeader>
      <CardContent>
        <AreaChart data={data} width={550} height={300}>
          <defs>
            <linearGradient id="moodGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
              <stop offset="50%" stopColor="#fbbf24" stopOpacity={0.6} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0.4} />
            </linearGradient>
          </defs>
          <XAxis dataKey="date" />
          <YAxis
            domain={[0, 5]}
            ticks={[1, 2, 3, 4, 5]}
            label={{ value: 'Mood Level', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip />
          <Legend />
          <Area
            type="monotone"
            dataKey="mood"
            stroke="#10b981"
            fill="url(#moodGradient)"
            strokeWidth={2}
            isAnimationActive={false}
            name="Mood"
          />
        </AreaChart>
      </CardContent>
    </Card>
  );
};

export const MoodChart = memo(MoodChartComponent);
