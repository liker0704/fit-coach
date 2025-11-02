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
import { TimePicker24 } from '@/components/ui/TimePicker24';
import { useToast } from '@/hooks/use-toast';
import { mealsService } from '@/services/modules/mealsService';
import type { Meal } from '@/types/models/health';
import { Plus, Pencil } from 'lucide-react';

const mealSchema = z.object({
  category: z.enum(['breakfast', 'lunch', 'dinner', 'snack']),
  time: z.string().optional(),
  calories: z.number().min(0).optional(),
  protein: z.number().min(0).optional(),
  carbs: z.number().min(0).optional(),
  fat: z.number().min(0).optional(),
  fiber: z.number().min(0).optional(),
  sugar: z.number().min(0).optional(),
  sodium: z.number().min(0).optional(),
  notes: z.string().optional(),
  photo_url: z.string().optional(),
});

type MealFormData = z.infer<typeof mealSchema>;

interface MealFormProps {
  dayId: number;
  meal?: Meal;
  onSuccess: () => void;
}

export function MealForm({ dayId, meal, onSuccess }: MealFormProps) {
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<MealFormData>({
    category: (meal?.category as MealFormData['category']) || 'breakfast',
    time: meal?.time || '',
    calories: meal?.calories || undefined,
    protein: meal?.protein || undefined,
    carbs: meal?.carbs || undefined,
    fat: meal?.fat || undefined,
    fiber: meal?.fiber || undefined,
    sugar: meal?.sugar || undefined,
    sodium: meal?.sodium || undefined,
    notes: meal?.notes || '',
    photo_url: meal?.photo_url || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    try {
      // Validate form data
      const validatedData = mealSchema.parse(formData);
      setLoading(true);

      // Transform empty strings to undefined for optional fields to match backend expectations
      const transformedData = {
        ...validatedData,
        time: validatedData.time || undefined,
        notes: validatedData.notes || undefined,
        photo_url: validatedData.photo_url || undefined,
      };

      if (meal) {
        // Update existing meal
        await mealsService.update(meal.id, transformedData);
        toast({
          title: 'Success',
          description: 'Meal updated successfully',
        });
      } else {
        // Create new meal
        await mealsService.create(dayId, transformedData);
        toast({
          title: 'Success',
          description: 'Meal added successfully',
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
          description: 'Failed to save meal',
          variant: 'destructive',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field: keyof MealFormData, value: any) => {
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

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {meal ? (
          <Button variant="ghost" size="sm">
            <Pencil className="h-4 w-4" />
          </Button>
        ) : (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Meal
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{meal ? 'Edit Meal' : 'Add Meal'}</DialogTitle>
          <DialogDescription>
            {meal ? 'Update meal details' : 'Add a new meal to your day'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {/* Category */}
            <div className="grid gap-2">
              <Label htmlFor="category">Category *</Label>
              <Select
                value={formData.category}
                onValueChange={(value) => updateField('category', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="breakfast">Breakfast</SelectItem>
                  <SelectItem value="lunch">Lunch</SelectItem>
                  <SelectItem value="dinner">Dinner</SelectItem>
                  <SelectItem value="snack">Snack</SelectItem>
                </SelectContent>
              </Select>
              {errors.category && (
                <p className="text-sm text-red-500">{errors.category}</p>
              )}
            </div>

            {/* Time */}
            <div className="grid gap-2">
              <TimePicker24
                label="Time"
                value={formData.time || ''}
                onChange={(value) => updateField('time', value)}
                placeholder="12:00"
              />
              {errors.time && (
                <p className="text-sm text-red-500">{errors.time}</p>
              )}
            </div>

            {/* Calories */}
            <div className="grid gap-2">
              <Label htmlFor="calories">Calories</Label>
              <Input
                id="calories"
                type="number"
                min="0"
                value={formData.calories || ''}
                onChange={(e) =>
                  updateField('calories', e.target.value ? Number(e.target.value) : undefined)
                }
                placeholder="e.g., 450"
              />
            </div>

            {/* Macros */}
            <div className="grid grid-cols-3 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="protein">Protein (g)</Label>
                <Input
                  id="protein"
                  type="number"
                  min="0"
                  value={formData.protein || ''}
                  onChange={(e) =>
                    updateField('protein', e.target.value ? Number(e.target.value) : undefined)
                  }
                  placeholder="e.g., 30"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="carbs">Carbs (g)</Label>
                <Input
                  id="carbs"
                  type="number"
                  min="0"
                  value={formData.carbs || ''}
                  onChange={(e) =>
                    updateField('carbs', e.target.value ? Number(e.target.value) : undefined)
                  }
                  placeholder="e.g., 45"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="fat">Fat (g)</Label>
                <Input
                  id="fat"
                  type="number"
                  min="0"
                  value={formData.fat || ''}
                  onChange={(e) =>
                    updateField('fat', e.target.value ? Number(e.target.value) : undefined)
                  }
                  placeholder="e.g., 15"
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
                placeholder="Additional notes about this meal..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : meal ? 'Update' : 'Add'} Meal
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
