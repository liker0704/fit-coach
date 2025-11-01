import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { exercisesService } from '@/services/modules/exercisesService';
import { ExerciseForm } from './ExerciseForm';
import type { Day, Exercise } from '@/types/models/health';
import { Dumbbell, Trash2, Clock, Flame, Heart } from 'lucide-react';

interface ExerciseSectionProps {
  day: Day;
  onUpdate: () => void;
}

export function ExerciseSection({ day, onUpdate }: ExerciseSectionProps) {
  const { toast } = useToast();
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const handleDelete = async (exerciseId: number) => {
    const confirmed = window.confirm('Are you sure you want to delete this exercise?');
    if (!confirmed) return;

    try {
      setDeletingId(exerciseId);
      await exercisesService.delete(exerciseId);
      toast({
        title: 'Success',
        description: 'Exercise deleted successfully',
      });
      onUpdate();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete exercise',
        variant: 'destructive',
      });
    } finally {
      setDeletingId(null);
    }
  };

  const renderExercise = (exercise: Exercise) => {
    const typeIcons: Record<string, string> = {
      running: '🏃',
      gym: '💪',
      yoga: '🧘',
      swimming: '🏊',
      cycling: '🚴',
      other: '🏋️',
    };

    const intensityStars = '⭐'.repeat(exercise.intensity || 0);

    return (
      <div key={exercise.id} className="py-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 space-y-1">
            <div className="flex items-center gap-2">
              <span>{typeIcons[exercise.exercise_type || 'other']}</span>
              <h4 className="font-medium">{exercise.name}</h4>
              {exercise.start_time && (
                <span className="flex items-center text-sm text-muted-foreground">
                  <Clock className="mr-1 h-3 w-3" />
                  {exercise.start_time}
                </span>
              )}
            </div>

            <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
              {exercise.duration && (
                <span>{exercise.duration} min</span>
              )}
              {exercise.distance && (
                <span>{exercise.distance} km</span>
              )}
              {exercise.intensity && (
                <span title={`Intensity: ${exercise.intensity}/5`}>
                  {intensityStars}
                </span>
              )}
              {exercise.calories_burned && (
                <span className="flex items-center">
                  <Flame className="mr-1 h-3 w-3" />
                  {exercise.calories_burned} cal
                </span>
              )}
              {exercise.heart_rate && (
                <span className="flex items-center">
                  <Heart className="mr-1 h-3 w-3" />
                  {exercise.heart_rate} bpm
                </span>
              )}
            </div>

            {exercise.notes && (
              <p className="text-sm text-muted-foreground italic">{exercise.notes}</p>
            )}
          </div>

          <div className="flex gap-1">
            <ExerciseForm dayId={day.id} exercise={exercise} onSuccess={onUpdate} />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleDelete(exercise.id)}
              disabled={deletingId === exercise.id}
            >
              <Trash2 className="h-4 w-4 text-red-500" />
            </Button>
          </div>
        </div>
      </div>
    );
  };

  const totalDuration = day.exercises.reduce((sum, ex) => sum + (ex.duration || 0), 0);
  const totalDistance = day.exercises.reduce((sum, ex) => sum + (ex.distance || 0), 0);
  const totalCalories = day.exercises.reduce((sum, ex) => sum + (ex.calories_burned || 0), 0);

  return (
    <div className="space-y-4">
      {/* Summary Card */}
      {day.exercises.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Exercise Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold">{day.exercises.length}</p>
                <p className="text-sm text-muted-foreground">Activities</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{totalDuration}</p>
                <p className="text-sm text-muted-foreground">Minutes</p>
              </div>
              {totalDistance > 0 && (
                <div>
                  <p className="text-2xl font-bold">{totalDistance.toFixed(1)}</p>
                  <p className="text-sm text-muted-foreground">km</p>
                </div>
              )}
              {totalCalories > 0 && (
                <div>
                  <p className="text-2xl font-bold">{totalCalories}</p>
                  <p className="text-sm text-muted-foreground">Calories</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Add Exercise Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Dumbbell className="h-5 w-5" />
          Exercise
        </h2>
        <ExerciseForm dayId={day.id} onSuccess={onUpdate} />
      </div>

      {/* Exercise List */}
      {day.exercises.length === 0 ? (
        <Card>
          <CardContent className="py-8">
            <p className="text-center text-muted-foreground">
              No exercises recorded yet. Click "Add Exercise" to get started.
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-0">
              {day.exercises.map((exercise, index) => (
                <div key={exercise.id}>
                  {renderExercise(exercise)}
                  {index < day.exercises.length - 1 && <Separator />}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
