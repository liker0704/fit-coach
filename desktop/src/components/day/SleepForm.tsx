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
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import { TimePicker24 } from '@/components/ui/TimePicker24';
import { useToast } from '@/hooks/use-toast';
import { sleepService } from '@/services/modules/sleepService';
import type { SleepRecord } from '@/types/models/health';
import { Plus, Pencil } from 'lucide-react';

const sleepSchema = z.object({
  bedtime: z.string().min(1, 'Bedtime is required'),
  wake_time: z.string().min(1, 'Wake time is required'),
  quality: z.number().min(1).max(5),
  notes: z.string().optional(),
});

type SleepFormData = z.infer<typeof sleepSchema>;

interface SleepFormProps {
  dayId: number;
  sleep?: SleepRecord;
  onSuccess: () => void;
}

// Calculate sleep duration in hours
const calculateDuration = (bedtime: string, wakeTime: string): number => {
  const [bedHour, bedMin] = bedtime.split(':').map(Number);
  const [wakeHour, wakeMin] = wakeTime.split(':').map(Number);

  let bedMinutes = bedHour * 60 + bedMin;
  let wakeMinutes = wakeHour * 60 + wakeMin;

  if (wakeMinutes < bedMinutes) {
    wakeMinutes += 24 * 60; // Add 24 hours for overnight sleep
  }

  const durationMinutes = wakeMinutes - bedMinutes;
  return durationMinutes / 60; // Return hours
};

// Format duration as "Xh Ymin"
const formatDuration = (hours: number): string => {
  const h = Math.floor(hours);
  const m = Math.round((hours - h) * 60);
  return `${h}h ${m}min`;
};

export function SleepForm({ dayId, sleep, onSuccess }: SleepFormProps) {
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<SleepFormData>({
    bedtime: sleep ? '22:30' : '',
    wake_time: sleep ? '06:00' : '',
    quality: sleep?.quality || 3,
    notes: sleep?.notes || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const duration = formData.bedtime && formData.wake_time
    ? calculateDuration(formData.bedtime, formData.wake_time)
    : 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    try {
      const validatedData = sleepSchema.parse(formData);
      const calculatedDuration = calculateDuration(validatedData.bedtime, validatedData.wake_time);

      setLoading(true);

      // Transform empty strings to undefined to prevent 422 validation errors
      const payload = {
        bedtime: validatedData.bedtime || undefined,
        wake_time: validatedData.wake_time || undefined,
        duration: calculatedDuration,
        quality: validatedData.quality,
        notes: validatedData.notes || undefined,
      };

      if (sleep) {
        await sleepService.update(sleep.id, payload);
        toast({
          title: 'Success',
          description: 'Sleep record updated successfully',
        });
      } else {
        await sleepService.create(dayId, payload);
        toast({
          title: 'Success',
          description: 'Sleep record added successfully',
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
          description: 'Failed to save sleep record',
          variant: 'destructive',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field: keyof SleepFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span key={i} className="text-2xl">
        {i < rating ? '⭐' : '☆'}
      </span>
    ));
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {sleep ? (
          <Button variant="ghost" size="sm">
            <Pencil className="h-4 w-4" />
          </Button>
        ) : (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Sleep
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{sleep ? 'Edit Sleep' : 'Add Sleep'}</DialogTitle>
          <DialogDescription>
            {sleep ? 'Update sleep details' : 'Record your sleep for the day'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {/* Bedtime */}
            <div className="grid gap-2">
              <TimePicker24
                label="Bedtime"
                value={formData.bedtime || ''}
                onChange={(value) => updateField('bedtime', value)}
                placeholder="22:00"
                required
              />
              {errors.bedtime && (
                <p className="text-sm text-red-500">{errors.bedtime}</p>
              )}
            </div>

            {/* Wake Time */}
            <div className="grid gap-2">
              <TimePicker24
                label="Wake Time"
                value={formData.wake_time || ''}
                onChange={(value) => updateField('wake_time', value)}
                placeholder="06:00"
                required
              />
              {errors.wake_time && (
                <p className="text-sm text-red-500">{errors.wake_time}</p>
              )}
            </div>

            {/* Duration Display */}
            {duration > 0 && (
              <div className="bg-muted p-3 rounded-md">
                <p className="text-sm text-muted-foreground">Duration</p>
                <p className="text-2xl font-bold">{formatDuration(duration)}</p>
              </div>
            )}

            {/* Quality Slider */}
            <div className="grid gap-2">
              <Label htmlFor="quality">Sleep Quality</Label>
              <div className="flex items-center justify-center py-2">
                {renderStars(formData.quality)}
              </div>
              <Slider
                id="quality"
                min={1}
                max={5}
                step={1}
                value={[formData.quality]}
                onValueChange={(value) => updateField('quality', value[0])}
                className="w-full"
              />
              <p className="text-sm text-center text-muted-foreground">
                {formData.quality}/5
              </p>
            </div>

            {/* Notes */}
            <div className="grid gap-2">
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => updateField('notes', e.target.value)}
                placeholder="Any notes about your sleep..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : sleep ? 'Update' : 'Add'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
