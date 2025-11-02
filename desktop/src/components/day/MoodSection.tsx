import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { moodService } from '@/services/modules/moodService';
import { MoodForm } from './MoodForm';
import { DeleteConfirmDialog } from '@/components/ui/DeleteConfirmDialog';
import type { Day } from '@/types/models/health';
import { Smile, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MoodSectionProps {
  day: Day;
  onUpdate: () => void;
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

const getMoodColor = (level: number): string => {
  if (level <= 2) return 'text-red-500';
  if (level === 3) return 'text-yellow-500';
  return 'text-green-500';
};

const getMoodBgColor = (level: number): string => {
  if (level <= 2) return 'bg-red-500/10';
  if (level === 3) return 'bg-yellow-500/10';
  return 'bg-green-500/10';
};

export function MoodSection({ day, onUpdate }: MoodSectionProps) {
  const { toast } = useToast();
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [moodToDelete, setMoodToDelete] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (moodId: number) => {
    setMoodToDelete(moodId);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!moodToDelete) return;

    try {
      setIsDeleting(true);
      setDeletingId(moodToDelete);
      await moodService.delete(moodToDelete);
      toast({
        title: 'Success',
        description: 'Mood record deleted successfully',
      });
      onUpdate();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete mood record',
        variant: 'destructive',
      });
    } finally {
      setIsDeleting(false);
      setDeletingId(null);
      setMoodToDelete(null);
      setDeleteDialogOpen(false);
    }
  };

  const moodRecord = day.mood_records && day.mood_records.length > 0
    ? day.mood_records[0]
    : null;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Smile className="h-5 w-5" />
          Mood
        </h2>
        {!moodRecord && <MoodForm dayId={day.id} onSuccess={onUpdate} />}
      </div>

      {/* Mood Record or Empty State */}
      {moodRecord ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>Today's Mood</span>
              <div className="flex gap-1">
                <MoodForm dayId={day.id} mood={moodRecord} onSuccess={onUpdate} />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDeleteClick(moodRecord.id)}
                  disabled={deletingId === moodRecord.id}
                >
                  <Trash2 className="h-4 w-4 text-red-500" />
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Mood Display */}
            <div className={cn('p-6 rounded-lg text-center', getMoodBgColor(moodRecord.rating))}>
              <div className="text-7xl mb-3">
                {MOOD_EMOJIS[moodRecord.rating]}
              </div>
              <p className={cn('text-2xl font-bold', getMoodColor(moodRecord.rating))}>
                {MOOD_LABELS[moodRecord.rating]}
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                {moodRecord.rating}/5
              </p>
            </div>

            {/* All Mood Levels */}
            <div className="flex justify-between px-2 py-3 bg-muted/50 rounded-lg">
              {[1, 2, 3, 4, 5].map((level) => (
                <div
                  key={level}
                  className={cn(
                    'flex flex-col items-center transition-all',
                    moodRecord.rating === level
                      ? 'scale-125 opacity-100'
                      : 'opacity-30'
                  )}
                >
                  <span className="text-2xl">{MOOD_EMOJIS[level]}</span>
                  <span className="text-xs mt-1">{level}</span>
                </div>
              ))}
            </div>

            {/* Notes */}
            {moodRecord.notes && (
              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground mb-2">Notes</p>
                <p className="text-sm italic">{moodRecord.notes}</p>
              </div>
            )}

            {/* Time */}
            {moodRecord.time && (
              <div className="text-center">
                <p className="text-xs text-muted-foreground">
                  Recorded at {moodRecord.time}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-12">
            <div className="text-center space-y-3">
              <Smile className="h-16 w-16 mx-auto text-muted-foreground opacity-50" />
              <div>
                <h3 className="text-lg font-semibold mb-1">No Mood Recorded</h3>
                <p className="text-muted-foreground text-sm">
                  Track how you're feeling today
                </p>
              </div>
              <div className="pt-2">
                <MoodForm dayId={day.id} onSuccess={onUpdate} />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleConfirmDelete}
        title="Delete Mood Record?"
        description="Are you sure you want to delete this mood record? This action cannot be undone."
        isDeleting={isDeleting}
      />
    </div>
  );
}
