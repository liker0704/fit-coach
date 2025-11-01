import { useState, useEffect } from 'react';
import { dayService } from '@/services/modules/dayService';
import { Button } from '@/components/ui/button';
import { LazyLoadChart } from '@/components/common/LazyLoadChart';
import { WeightChart } from '@/components/stats/WeightChart';
import { ActivityChart } from '@/components/stats/ActivityChart';
import { NutritionChart } from '@/components/stats/NutritionChart';
import { WaterChart } from '@/components/stats/WaterChart';
import { SleepChart } from '@/components/stats/SleepChart';
import { MoodChart } from '@/components/stats/MoodChart';
import { EffortChart } from '@/components/stats/EffortChart';
import { format, subDays, subMonths } from 'date-fns';
import type { Day } from '@/types/models/health';

export default function StatsPage() {
  const [days, setDays] = useState<Day[]>([]);
  const [loading, setLoading] = useState(false);
  const [period, setPeriod] = useState<'week' | 'month' | 'custom'>('week');
  const [startDate, setStartDate] = useState(subDays(new Date(), 7));
  const [endDate, setEndDate] = useState(new Date());

  useEffect(() => {
    fetchDays();
  }, [startDate, endDate]);

  const fetchDays = async () => {
    setLoading(true);
    try {
      const formattedStartDate = format(startDate, 'yyyy-MM-dd');
      const formattedEndDate = format(endDate, 'yyyy-MM-dd');
      const data = await dayService.getDays(
        formattedStartDate,
        formattedEndDate
      );
      // Sort by date ascending
      const sortedData = data.sort(
        (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
      );
      setDays(sortedData);
    } catch (error) {
      console.error('Failed to fetch days:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePeriodChange = (newPeriod: 'week' | 'month') => {
    setPeriod(newPeriod);
    if (newPeriod === 'week') {
      setStartDate(subDays(new Date(), 7));
      setEndDate(new Date());
    } else if (newPeriod === 'month') {
      setStartDate(subMonths(new Date(), 1));
      setEndDate(new Date());
    }
  };

  const getPeriodLabel = () => {
    if (period === 'week') {
      return 'Last 7 days';
    } else if (period === 'month') {
      return 'Last 30 days';
    } else {
      return `${format(startDate, 'MMM dd')} - ${format(endDate, 'MMM dd')}`;
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Statistics</h1>

      {/* Filters */}
      <div className="mb-6">
        <div className="flex gap-2 mb-2">
          <Button
            variant={period === 'week' ? 'default' : 'outline'}
            onClick={() => handlePeriodChange('week')}
          >
            Week
          </Button>
          <Button
            variant={period === 'month' ? 'default' : 'outline'}
            onClick={() => handlePeriodChange('month')}
          >
            Month
          </Button>
        </div>
        <p className="text-sm text-muted-foreground">
          Selected: {getPeriodLabel()}
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center p-12">
          <p className="text-muted-foreground">Loading statistics...</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && days.length === 0 && (
        <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-lg">
          <p className="text-xl font-semibold mb-2">No data available</p>
          <p className="text-muted-foreground text-center">
            Start tracking your daily activities to see statistics here.
            <br />
            Go to the Day View to add meals, exercises, and more.
          </p>
        </div>
      )}

      {/* Charts Grid */}
      {!loading && days.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LazyLoadChart height={300}>
            <WeightChart days={days} />
          </LazyLoadChart>
          <LazyLoadChart height={300}>
            <ActivityChart days={days} />
          </LazyLoadChart>
          <LazyLoadChart height={300}>
            <NutritionChart days={days} />
          </LazyLoadChart>
          <LazyLoadChart height={300}>
            <WaterChart days={days} />
          </LazyLoadChart>
          <LazyLoadChart height={300}>
            <SleepChart days={days} />
          </LazyLoadChart>
          <LazyLoadChart height={300}>
            <MoodChart days={days} />
          </LazyLoadChart>
          <LazyLoadChart height={300}>
            <EffortChart days={days} />
          </LazyLoadChart>
        </div>
      )}
    </div>
  );
}
