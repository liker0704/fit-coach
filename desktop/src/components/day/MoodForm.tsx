import { useState } from 'react';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
import { useToast } from '@/hooks/use-toast';
import { moodService } from '@/services/modules/moodService';
import type { MoodRecord } from '@/types/models/health';
import { Plus, Pencil } from 'lucide-react';
import { cn } from '@/lib/utils';

const moodSchema = z.object({
  rating: z.number().min(1).max(5),
  time: z.string().optional(),
  energy_level: z.number().min(1).max(5).optional(),
  stress_level: z.number().min(1).max(5).optional(),
  anxiety_level: z.number().min(1).max(5).optional(),
  tags: z.array(z.string()).optional(),
  notes: z.string().optional(),
});

type MoodFormData = z.infer<typeof moodSchema>;

interface MoodFormProps {
  dayId: number;
  mood?: MoodRecord;
  onSuccess: () => void;
}

const MOOD_EMOJIS: Record<number, string> = {
  1: '😢',
  2: '😕',
  3: '😐',
  4: '🙂',
  5: '😊',
};

const MOOD_LABELS: Record<number, string> = {
  1: 'Very Bad',
  2: 'Bad',
  3: 'Okay',
  4: 'Good',
  5: 'Great',
};

const POSITIVE_TAGS = ['Productive', 'Energized', 'Focused', 'Happy', 'Motivated'];
const NEGATIVE_TAGS = ['Stressed', 'Anxious', 'Tired', 'Sad', 'Frustrated'];

export function MoodForm({ dayId, mood, onSuccess }: MoodFormProps) {
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  // Parse tags from notes field (since backend doesn't have tags field yet)
  const parsedTags: string[] = [];

  const [formData, setFormData] = useState<MoodFormData>({
    rating: mood?.rating || 3,
    tags: mood?.tags || parsedTags,
    notes: mood?.notes || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    try {
      const validatedData = moodSchema.parse(formData);
      setLoading(true);

      // Prepare payload with required time field and convert empty strings to undefined
      const payload = {
        time: validatedData.time || new Date().toISOString(),
        rating: validatedData.rating,
        energy_level: validatedData.energy_level,
        stress_level: validatedData.stress_level,
        anxiety_level: validatedData.anxiety_level,
        tags: validatedData.tags && validatedData.tags.length > 0 ? validatedData.tags : undefined,
        notes: validatedData.notes || undefined,
      };

      if (mood) {
        await moodService.update(mood.id, payload);
        toast({
          title: 'Success',
          description: 'Mood updated successfully',
        });
      } else {
        await moodService.create(dayId, payload);
        toast({
          title: 'Success',
          description: 'Mood recorded successfully',
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
          description: 'Failed to save mood',
          variant: 'destructive',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field: keyof MoodFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const toggleTag = (tag: string) => {
    const currentTags = formData.tags || [];
    if (currentTags.includes(tag)) {
      updateField('tags', currentTags.filter((t) => t !== tag));
    } else {
      updateField('tags', [...currentTags, tag]);
    }
  };

  const getMoodColor = (level: number): string => {
    if (level <= 2) return 'text-red-500';
    if (level === 3) return 'text-yellow-500';
    return 'text-green-500';
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {mood ? (
          <Button variant="ghost" size="sm">
            <Pencil className="h-4 w-4" />
          </Button>
        ) : (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Mood
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{mood ? 'Edit Mood' : 'Record Mood'}</DialogTitle>
          <DialogDescription>
            How are you feeling today?
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-6 py-4">
            {/* Mood Level Selector */}
            <div className="grid gap-3">
              <Label>Mood Level *</Label>
              <div className="flex justify-between gap-2">
                {[1, 2, 3, 4, 5].map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => updateField('rating', level)}
                    className={cn(
                      'flex flex-col items-center gap-2 p-3 rounded-lg border-2 transition-all hover:scale-105',
                      formData.rating === level
                        ? 'border-primary bg-primary/10 scale-105'
                        : 'border-muted hover:border-muted-foreground/30'
                    )}
                  >
                    <span className="text-4xl">{MOOD_EMOJIS[level]}</span>
                    <span className="text-xs font-medium">{level}</span>
                  </button>
                ))}
              </div>
              <p className={cn('text-center font-medium', getMoodColor(formData.rating))}>
                {MOOD_LABELS[formData.rating]}
              </p>
            </div>

            {/* Tags */}
            <div className="grid gap-3">
              <Label>Tags (Optional)</Label>
              <div className="space-y-2">
                <div>
                  <p className="text-xs text-muted-foreground mb-2">Positive</p>
                  <div className="flex flex-wrap gap-2">
                    {POSITIVE_TAGS.map((tag) => (
                      <Badge
                        key={tag}
                        variant={formData.tags?.includes(tag) ? 'default' : 'outline'}
                        className="cursor-pointer"
                        onClick={() => toggleTag(tag)}
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-2">Negative</p>
                  <div className="flex flex-wrap gap-2">
                    {NEGATIVE_TAGS.map((tag) => (
                      <Badge
                        key={tag}
                        variant={formData.tags?.includes(tag) ? 'default' : 'outline'}
                        className="cursor-pointer"
                        onClick={() => toggleTag(tag)}
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Notes */}
            <div className="grid gap-2">
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => updateField('notes', e.target.value)}
                placeholder="What's on your mind today?"
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : mood ? 'Update' : 'Save'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
