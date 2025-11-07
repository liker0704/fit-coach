import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { mealsService } from '@/services/modules/mealsService';
import { MealForm } from './MealForm';
import { MealPhotoUpload } from './MealPhotoUpload';
import { DeleteConfirmDialog } from '@/components/ui/DeleteConfirmDialog';
import type { Day, Meal } from '@/types/models/health';
import { Utensils, Trash2, Clock } from 'lucide-react';

interface MealsSectionProps {
  day: Day;
  onUpdate: () => void;
}

export function MealsSection({ day, onUpdate }: MealsSectionProps) {
  const { toast } = useToast();
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [mealToDelete, setMealToDelete] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (mealId: number) => {
    setMealToDelete(mealId);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!mealToDelete) return;

    try {
      setIsDeleting(true);
      setDeletingId(mealToDelete);
      await mealsService.delete(mealToDelete);
      toast({
        title: 'Success',
        description: 'Meal deleted successfully',
      });
      onUpdate();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete meal',
        variant: 'destructive',
      });
    } finally {
      setIsDeleting(false);
      setDeletingId(null);
      setMealToDelete(null);
      setDeleteDialogOpen(false);
    }
  };

  // Group meals by category
  const mealsByCategory = {
    breakfast: day.meals.filter((m) => m.category === 'breakfast'),
    lunch: day.meals.filter((m) => m.category === 'lunch'),
    dinner: day.meals.filter((m) => m.category === 'dinner'),
    snack: day.meals.filter((m) => m.category === 'snack'),
  };

  const renderMeal = (meal: Meal) => {
    const totalCalories = meal.calories || 0;
    const protein = meal.protein || 0;
    const carbs = meal.carbs || 0;
    const fat = meal.fat || 0;

    return (
      <div key={meal.id} className="py-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 space-y-1">
            <div className="flex items-center gap-2">
              <h4 className="font-medium capitalize">{meal.category}</h4>
              {meal.time && (
                <span className="flex items-center text-sm text-muted-foreground">
                  <Clock className="mr-1 h-3 w-3" />
                  {meal.time}
                </span>
              )}
            </div>

            {totalCalories > 0 && (
              <p className="text-sm text-muted-foreground">
                {totalCalories} calories
              </p>
            )}

            {(protein > 0 || carbs > 0 || fat > 0) && (
              <p className="text-xs text-muted-foreground">
                P: {protein}g | C: {carbs}g | F: {fat}g
              </p>
            )}

            {meal.notes && (
              <p className="text-sm text-muted-foreground italic">{meal.notes}</p>
            )}
          </div>

          <div className="flex gap-1">
            <MealForm dayId={day.id} meal={meal} onSuccess={onUpdate} />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleDeleteClick(meal.id)}
              disabled={deletingId === meal.id}
            >
              <Trash2 className="h-4 w-4 text-red-500" />
            </Button>
          </div>
        </div>
      </div>
    );
  };

  const renderCategory = (category: string, meals: Meal[]) => {
    if (meals.length === 0) return null;

    const categoryIcons: Record<string, string> = {
      breakfast: '🌅',
      lunch: '🍽️',
      dinner: '🌙',
      snack: '🍎',
    };

    return (
      <div key={category} className="mb-6">
        <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
          <span>{categoryIcons[category]}</span>
          <span className="capitalize">{category}</span>
          <span className="text-sm text-muted-foreground">({meals.length})</span>
        </h3>
        <div className="space-y-0">
          {meals.map((meal, index) => (
            <div key={meal.id}>
              {renderMeal(meal)}
              {index < meals.length - 1 && <Separator />}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const totalCalories = day.meals.reduce((sum, meal) => sum + (meal.calories || 0), 0);
  const totalProtein = day.meals.reduce((sum, meal) => sum + (meal.protein || 0), 0);
  const totalCarbs = day.meals.reduce((sum, meal) => sum + (meal.carbs || 0), 0);
  const totalFat = day.meals.reduce((sum, meal) => sum + (meal.fat || 0), 0);

  return (
    <div className="space-y-4">
      {/* Summary Card */}
      {day.meals.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Daily Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold">{totalCalories}</p>
                <p className="text-sm text-muted-foreground">Calories</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{totalProtein}g</p>
                <p className="text-sm text-muted-foreground">Protein</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{totalCarbs}g</p>
                <p className="text-sm text-muted-foreground">Carbs</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{totalFat}g</p>
                <p className="text-sm text-muted-foreground">Fat</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Add Meal Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Utensils className="h-5 w-5" />
          Meals
        </h2>
        <div className="flex gap-2">
          <MealPhotoUpload dayId={day.id} onSuccess={onUpdate} />
          <MealForm dayId={day.id} onSuccess={onUpdate} />
        </div>
      </div>

      {/* Meals by Category */}
      {day.meals.length === 0 ? (
        <Card>
          <CardContent className="py-8">
            <p className="text-center text-muted-foreground">
              No meals recorded yet. Click "Add Meal" to get started.
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="pt-6">
            {renderCategory('breakfast', mealsByCategory.breakfast)}
            {renderCategory('lunch', mealsByCategory.lunch)}
            {renderCategory('dinner', mealsByCategory.dinner)}
            {renderCategory('snack', mealsByCategory.snack)}
          </CardContent>
        </Card>
      )}

      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleConfirmDelete}
        title="Delete Meal?"
        description="Are you sure you want to delete this meal? This action cannot be undone."
        isDeleting={isDeleting}
      />
    </div>
  );
}
