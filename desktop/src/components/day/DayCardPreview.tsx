import { format } from 'date-fns';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import type { Day } from '@/types/models/health';

interface DayCardPreviewProps {
  day: Day;
}

export function DayCardPreview({ day }: DayCardPreviewProps) {
  const navigate = useNavigate();

  // Aggregate data
  const mealCount = day.meals.length;
  const totalCalories = day.meals.reduce(
    (sum, meal) => sum + (meal.calories || 0),
    0
  );

  const exerciseCount = day.exercises.length;
  const totalDuration = day.exercises.reduce(
    (sum, exercise) => sum + (exercise.duration || 0),
    0
  );

  const totalWater = day.water_intakes.reduce(
    (sum, intake) => sum + intake.amount,
    0
  );

  const sleepHours = day.sleep_records[0]?.duration || 0;
  const moodLevel = day.mood_records[0]?.rating || 0;
  const effortScore = day.effort_score || 0;

  // Format date
  const dateObj = new Date(day.date);
  const formattedDate = format(dateObj, 'EEEE, MMM d, yyyy');

  // Generate star rating for effort score
  const stars = '⭐'.repeat(Math.round(effortScore / 2));

  const handleOpenDay = () => {
    navigate(`/day/${day.id}`);
  };

  return (
    <Card className="w-full max-w-sm">
      <CardHeader>
        <CardTitle className="text-lg">{formattedDate}</CardTitle>
        <p className="text-sm text-muted-foreground">
          Effort: {effortScore.toFixed(1)}/10 {stars}
        </p>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-center gap-2 text-sm">
          <span>🍽️</span>
          <span>
            {mealCount} meal{mealCount !== 1 ? 's' : ''} ({totalCalories} kcal)
          </span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span>💪</span>
          <span>
            {exerciseCount} exercise{exerciseCount !== 1 ? 's' : ''} (
            {totalDuration} min)
          </span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span>💧</span>
          <span>
            {totalWater.toFixed(1)}L / 2.5L
          </span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span>😴</span>
          <span>{sleepHours}h sleep</span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span>😊</span>
          <span>Mood: {moodLevel}/5</span>
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={handleOpenDay} className="w-full">
          Open Day
        </Button>
      </CardFooter>
    </Card>
  );
}
