import { useState } from 'react';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import { useToast } from '@/hooks/use-toast';
import { exercisesService } from '@/services/modules/exercisesService';
import type { Exercise } from '@/types/models/health';
import { Plus, Pencil } from 'lucide-react';

const exerciseSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  exercise_type: z.enum(['running', 'gym', 'yoga', 'swimming', 'cycling', 'other']),
  start_time: z.string().min(1, 'Start time is required'),
  duration: z.number().min(1, 'Duration must be at least 1 minute'),
  distance: z.number().min(0).optional(),
  intensity: z.number().min(1).max(5),
  calories_burned: z.number().min(0).optional(),
  heart_rate: z.number().min(0).optional(),
  notes: z.string().optional(),
});

type ExerciseFormData = z.infer<typeof exerciseSchema>;

interface ExerciseFormProps {
  dayId: number;
  exercise?: Exercise;
  onSuccess: () => void;
}

export function ExerciseForm({ dayId, exercise, onSuccess }: ExerciseFormProps) {
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<ExerciseFormData>({
    name: exercise?.name || '',
    exercise_type: (exercise?.exercise_type as ExerciseFormData['exercise_type']) || 'running',
    start_time: exercise?.start_time || '',
    duration: exercise?.duration || 30,
    distance: exercise?.distance || undefined,
    intensity: exercise?.intensity || 3,
    calories_burned: exercise?.calories_burned || undefined,
    heart_rate: exercise?.heart_rate || undefined,
    notes: exercise?.notes || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    try {
      // Validate form data
      const validatedData = exerciseSchema.parse(formData);
      setLoading(true);

      if (exercise) {
        // Update existing exercise
        await exercisesService.update(exercise.id, validatedData);
        toast({
          title: 'Success',
          description: 'Exercise updated successfully',
        });
      } else {
        // Create new exercise
        await exercisesService.create(dayId, validatedData);
        toast({
          title: 'Success',
          description: 'Exercise added successfully',
        });
      }

      setOpen(false);
      onSuccess();
    } catch (error) {
      if (error instanceof z.ZodError) {
        const fieldErrors: Record<string, string> = {};
        error.issues.forEach((err: z.ZodIssue) => {
          if (err.path[0]) {
            fieldErrors[err.path[0].toString()] = err.message;
          }
        });
        setErrors(fieldErrors);
      } else {
        toast({
          title: 'Error',
          description: 'Failed to save exercise',
          variant: 'destructive',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field: keyof ExerciseFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const intensityLabels = ['Very Light', 'Light', 'Moderate', 'Hard', 'Very Hard'];

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {exercise ? (
          <Button variant="ghost" size="sm">
            <Pencil className="h-4 w-4" />
          </Button>
        ) : (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Exercise
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{exercise ? 'Edit Exercise' : 'Add Exercise'}</DialogTitle>
          <DialogDescription>
            {exercise ? 'Update exercise details' : 'Add a new exercise to your day'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {/* Exercise Type */}
            <div className="grid gap-2">
              <Label htmlFor="exercise_type">Type *</Label>
              <Select
                value={formData.exercise_type}
                onValueChange={(value) => updateField('exercise_type', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="running">Running</SelectItem>
                  <SelectItem value="gym">Gym</SelectItem>
                  <SelectItem value="yoga">Yoga</SelectItem>
                  <SelectItem value="swimming">Swimming</SelectItem>
                  <SelectItem value="cycling">Cycling</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
              {errors.exercise_type && (
                <p className="text-sm text-red-500">{errors.exercise_type}</p>
              )}
            </div>

            {/* Name */}
            <div className="grid gap-2">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => updateField('name', e.target.value)}
                placeholder="e.g., Morning Run"
              />
              {errors.name && (
                <p className="text-sm text-red-500">{errors.name}</p>
              )}
            </div>

            {/* Start Time */}
            <div className="grid gap-2">
              <Label htmlFor="start_time">Start Time *</Label>
              <Input
                id="start_time"
                type="time"
                value={formData.start_time}
                onChange={(e) => updateField('start_time', e.target.value)}
              />
              {errors.start_time && (
                <p className="text-sm text-red-500">{errors.start_time}</p>
              )}
            </div>

            {/* Duration and Distance */}
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="duration">Duration (minutes) *</Label>
                <Input
                  id="duration"
                  type="number"
                  min="1"
                  value={formData.duration}
                  onChange={(e) =>
                    updateField('duration', e.target.value ? Number(e.target.value) : 1)
                  }
                  placeholder="e.g., 30"
                />
                {errors.duration && (
                  <p className="text-sm text-red-500">{errors.duration}</p>
                )}
              </div>
              <div className="grid gap-2">
                <Label htmlFor="distance">Distance (km)</Label>
                <Input
                  id="distance"
                  type="number"
                  min="0"
                  step="0.1"
                  value={formData.distance || ''}
                  onChange={(e) =>
                    updateField('distance', e.target.value ? Number(e.target.value) : undefined)
                  }
                  placeholder="e.g., 5.2"
                />
              </div>
            </div>

            {/* Intensity */}
            <div className="grid gap-2">
              <Label htmlFor="intensity">
                Intensity * - {intensityLabels[formData.intensity - 1]}
              </Label>
              <Slider
                id="intensity"
                min={1}
                max={5}
                step={1}
                value={[formData.intensity]}
                onValueChange={(value) => updateField('intensity', value[0])}
                className="py-4"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Very Light</span>
                <span>Very Hard</span>
              </div>
              {errors.intensity && (
                <p className="text-sm text-red-500">{errors.intensity}</p>
              )}
            </div>

            {/* Calories and Heart Rate */}
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="calories_burned">Calories Burned</Label>
                <Input
                  id="calories_burned"
                  type="number"
                  min="0"
                  value={formData.calories_burned || ''}
                  onChange={(e) =>
                    updateField('calories_burned', e.target.value ? Number(e.target.value) : undefined)
                  }
                  placeholder="e.g., 300"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="heart_rate">Heart Rate (bpm)</Label>
                <Input
                  id="heart_rate"
                  type="number"
                  min="0"
                  value={formData.heart_rate || ''}
                  onChange={(e) =>
                    updateField('heart_rate', e.target.value ? Number(e.target.value) : undefined)
                  }
                  placeholder="e.g., 145"
                />
              </div>
            </div>

            {/* Notes */}
            <div className="grid gap-2">
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => updateField('notes', e.target.value)}
                placeholder="Additional notes about this exercise..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : exercise ? 'Update' : 'Add'} Exercise
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
