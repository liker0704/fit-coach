import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  format,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  isSameDay,
  isToday,
  addMonths,
  subMonths,
  startOfWeek,
  endOfWeek,
  isSameMonth,
} from 'date-fns';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { dayService } from '@/services/modules/dayService';
import type { Day } from '@/types/models/health';
import { cn } from '@/lib/utils';

export default function CalendarPage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [days, setDays] = useState<Day[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch days for current month
  useEffect(() => {
    const fetchDays = async () => {
      setLoading(true);
      try {
        const startDate = startOfMonth(currentMonth);
        const endDate = endOfMonth(currentMonth);
        const response = await dayService.getDays(
          format(startDate, 'yyyy-MM-dd'),
          format(endDate, 'yyyy-MM-dd')
        );
        setDays(response);
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to load calendar',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    };
    fetchDays();
  }, [currentMonth, toast]);

  // Generate calendar grid (complete weeks)
  const generateCalendarDays = () => {
    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(currentMonth);
    const calendarStart = startOfWeek(monthStart, { weekStartsOn: 1 }); // Monday
    const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });

    return eachDayOfInterval({ start: calendarStart, end: calendarEnd });
  };

  const calendarDays = generateCalendarDays();

  // Find day data for a given date
  const findDayData = (date: Date): Day | undefined => {
    return days.find((day) => isSameDay(new Date(day.date), date));
  };

  // Get color classes based on effort score
  const getEffortColorClasses = (effortScore?: number | null) => {
    if (effortScore === null || effortScore === undefined) {
      return 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700';
    }
    if (effortScore >= 8) {
      return 'bg-green-100 dark:bg-green-900/40 border-green-500 dark:border-green-600';
    }
    if (effortScore >= 5) {
      return 'bg-yellow-100 dark:bg-yellow-900/40 border-yellow-500 dark:border-yellow-600';
    }
    if (effortScore >= 3) {
      return 'bg-orange-100 dark:bg-orange-900/40 border-orange-500 dark:border-orange-600';
    }
    return 'bg-red-100 dark:bg-red-900/40 border-red-500 dark:border-red-600';
  };

  // Handle day click
  const handleDayClick = async (date: Date) => {
    const dayData = findDayData(date);

    if (dayData) {
      navigate(`/day/${dayData.id}`);
    } else {
      // Create new day if doesn't exist
      try {
        const newDay = await dayService.createDay(format(date, 'yyyy-MM-dd'));
        navigate(`/day/${newDay.id}`);
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to create day',
          variant: 'destructive',
        });
      }
    }
  };

  // Navigation handlers
  const handlePreviousMonth = () => {
    setCurrentMonth((prev) => subMonths(prev, 1));
  };

  const handleNextMonth = () => {
    setCurrentMonth((prev) => addMonths(prev, 1));
  };

  const handleToday = () => {
    setCurrentMonth(new Date());
  };

  // Weekday headers
  const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  return (
    <div className="h-full flex flex-col overflow-hidden p-4 md:p-6 max-w-6xl mx-auto">
      <Card className="h-full flex flex-col overflow-hidden">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl font-bold">
              {format(currentMonth, 'MMMM yyyy')}
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="icon"
                onClick={handlePreviousMonth}
                disabled={loading}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                onClick={handleToday}
                disabled={loading}
              >
                <Calendar className="h-4 w-4 mr-2" />
                Today
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={handleNextMonth}
                disabled={loading}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto min-h-0 pb-4">
          {loading ? (
            <div className="flex items-center justify-center h-96">
              <div className="text-muted-foreground">Loading calendar...</div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Weekday headers */}
              <div className="grid grid-cols-7 gap-2">
                {weekDays.map((day) => (
                  <div
                    key={day}
                    className="text-center text-sm font-semibold text-muted-foreground py-2"
                  >
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar grid */}
              <div className="grid grid-cols-7 gap-2">
                {calendarDays.map((date, index) => {
                  const dayData = findDayData(date);
                  const isCurrentMonth = isSameMonth(date, currentMonth);
                  const isTodayDate = isToday(date);

                  return (
                    <button
                      key={index}
                      onClick={() => handleDayClick(date)}
                      className={cn(
                        'relative min-h-[60px] sm:min-h-[70px] md:aspect-square rounded-lg border-2 p-2 transition-all hover:shadow-md',
                        getEffortColorClasses(dayData?.effort_score),
                        !isCurrentMonth && 'opacity-40 dark:opacity-50',
                        isTodayDate && 'ring-2 ring-primary ring-offset-2',
                        'flex flex-col items-center justify-center'
                      )}
                    >
                      <span
                        className={cn(
                          'text-sm font-medium',
                          !isCurrentMonth
                            ? 'text-gray-400 dark:text-gray-600'
                            : 'text-gray-900 dark:text-gray-100'
                        )}
                      >
                        {format(date, 'd')}
                      </span>
                      {dayData && (
                        <div className="mt-1 text-xs">
                          {dayData.effort_score !== null &&
                            dayData.effort_score !== undefined && (
                              <span className="font-semibold">
                                {dayData.effort_score.toFixed(0)}
                              </span>
                            )}
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>

              {/* Empty state */}
              {days.length === 0 && (
                <div className="text-center py-12">
                  <Calendar className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">
                    No tracked days yet
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    Start tracking your daily activities by clicking on any day
                  </p>
                  <Button onClick={handleToday}>Start Tracking Today</Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
