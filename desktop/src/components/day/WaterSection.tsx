import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { waterService } from '@/services/modules/waterService';
import { WaterAddDialog } from './WaterAddDialog';
import type { Day, WaterIntake } from '@/types/models/health';
import { Droplets, Trash2, Plus, Clock } from 'lucide-react';

interface WaterSectionProps {
  day: Day;
  onUpdate: () => void;
}

export function WaterSection({ day, onUpdate }: WaterSectionProps) {
  const { toast } = useToast();
  const [addingAmount, setAddingAmount] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const DAILY_GOAL = 2.5; // 2.5L default goal

  // Calculate total water intake
  const totalWater = day.water_intakes.reduce((sum, intake) => sum + intake.amount, 0);
  const percentage = Math.min((totalWater / DAILY_GOAL) * 100, 100);

  const handleQuickAdd = async (amount: number) => {
    try {
      setAddingAmount(amount);

      // Get current time
      const now = new Date();
      const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:00`;

      await waterService.create(day.id, { amount, time });

      toast({
        title: 'Success',
        description: `Added ${amount}L of water`,
      });

      onUpdate();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to add water intake',
        variant: 'destructive',
      });
    } finally {
      setAddingAmount(null);
    }
  };

  const handleDelete = async (waterIntakeId: number) => {
    const confirmed = window.confirm('Are you sure you want to delete this water intake?');
    if (!confirmed) return;

    try {
      setDeletingId(waterIntakeId);
      await waterService.delete(waterIntakeId);
      toast({
        title: 'Success',
        description: 'Water intake deleted successfully',
      });
      onUpdate();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete water intake',
        variant: 'destructive',
      });
    } finally {
      setDeletingId(null);
    }
  };

  const renderWaterIntake = (intake: WaterIntake) => {
    return (
      <div key={intake.id} className="flex items-center justify-between py-2">
        <div className="flex items-center gap-2">
          <Droplets className="h-4 w-4 text-blue-500" />
          <span className="font-medium">{intake.amount}L</span>
          {intake.time && (
            <span className="flex items-center text-sm text-muted-foreground">
              <Clock className="mr-1 h-3 w-3" />
              {intake.time.slice(0, 5)}
            </span>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleDelete(intake.id)}
          disabled={deletingId === intake.id}
        >
          <Trash2 className="h-4 w-4 text-red-500" />
        </Button>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Progress Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Droplets className="h-5 w-5 text-blue-500" />
            Water Intake
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Daily Progress</span>
              <span className="font-medium">
                {totalWater.toFixed(1)}L / {DAILY_GOAL}L
              </span>
            </div>
            <Progress value={percentage} className="h-3" />
            <p className="text-xs text-muted-foreground text-center">
              {percentage.toFixed(0)}% of daily goal
            </p>
          </div>

          {/* Quick Add Buttons */}
          <div className="space-y-2">
            <p className="text-sm font-medium">Quick Add</p>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleQuickAdd(0.25)}
                disabled={addingAmount === 0.25}
              >
                <Plus className="mr-1 h-3 w-3" />
                0.25L
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleQuickAdd(0.5)}
                disabled={addingAmount === 0.5}
              >
                <Plus className="mr-1 h-3 w-3" />
                0.5L
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleQuickAdd(1.0)}
                disabled={addingAmount === 1.0}
              >
                <Plus className="mr-1 h-3 w-3" />
                1.0L
              </Button>
              <WaterAddDialog dayId={day.id} onSuccess={onUpdate} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Water Intake History */}
      {day.water_intakes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-0">
              {day.water_intakes
                .sort((a, b) => {
                  // Sort by time, newest first
                  if (!a.time) return 1;
                  if (!b.time) return -1;
                  return b.time.localeCompare(a.time);
                })
                .map((intake, index) => (
                  <div key={intake.id}>
                    {renderWaterIntake(intake)}
                    {index < day.water_intakes.length - 1 && <Separator />}
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {day.water_intakes.length === 0 && (
        <Card>
          <CardContent className="py-8">
            <p className="text-center text-muted-foreground">
              No water intake recorded yet. Use quick add buttons to track your water consumption.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
