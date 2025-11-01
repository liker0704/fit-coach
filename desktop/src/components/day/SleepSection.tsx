import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { sleepService } from '@/services/modules/sleepService';
import { SleepForm } from './SleepForm';
import type { Day } from '@/types/models/health';
import { Moon, Trash2 } from 'lucide-react';

interface SleepSectionProps {
  day: Day;
  onUpdate: () => void;
}

// Format duration as "Xh Ymin"
const formatDuration = (hours: number): string => {
  const h = Math.floor(hours);
  const m = Math.round((hours - h) * 60);
  return `${h}h ${m}min`;
};

// Render stars for quality
const renderStars = (rating: number) => {
  return Array.from({ length: 5 }, (_, i) => (
    <span key={i} className="text-xl">
      {i < rating ? '⭐' : '☆'}
    </span>
  ));
};

export function SleepSection({ day, onUpdate }: SleepSectionProps) {
  const { toast } = useToast();
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const handleDelete = async (sleepId: number) => {
    const confirmed = window.confirm('Are you sure you want to delete this sleep record?');
    if (!confirmed) return;

    try {
      setDeletingId(sleepId);
      await sleepService.delete(sleepId);
      toast({
        title: 'Success',
        description: 'Sleep record deleted successfully',
      });
      onUpdate();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete sleep record',
        variant: 'destructive',
      });
    } finally {
      setDeletingId(null);
    }
  };

  const sleepRecord = day.sleep_records && day.sleep_records.length > 0
    ? day.sleep_records[0]
    : null;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Moon className="h-5 w-5" />
          Sleep
        </h2>
        {!sleepRecord && <SleepForm dayId={day.id} onSuccess={onUpdate} />}
      </div>

      {/* Sleep Record or Empty State */}
      {sleepRecord ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>Sleep Record</span>
              <div className="flex gap-1">
                <SleepForm dayId={day.id} sleep={sleepRecord} onSuccess={onUpdate} />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(sleepRecord.id)}
                  disabled={deletingId === sleepRecord.id}
                >
                  <Trash2 className="h-4 w-4 text-red-500" />
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Duration */}
            <div className="bg-primary/10 p-4 rounded-lg text-center">
              <p className="text-sm text-muted-foreground mb-1">Total Sleep</p>
              <p className="text-3xl font-bold">
                {formatDuration(sleepRecord.duration)}
              </p>
            </div>

            {/* Quality */}
            {sleepRecord.quality && (
              <div className="text-center space-y-2">
                <p className="text-sm text-muted-foreground">Sleep Quality</p>
                <div className="flex items-center justify-center gap-1">
                  {renderStars(sleepRecord.quality)}
                </div>
                <p className="text-sm font-medium">
                  {sleepRecord.quality}/5
                </p>
              </div>
            )}

            {/* Notes */}
            {sleepRecord.notes && (
              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground mb-2">Notes</p>
                <p className="text-sm italic">{sleepRecord.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-12">
            <div className="text-center space-y-3">
              <Moon className="h-16 w-16 mx-auto text-muted-foreground opacity-50" />
              <div>
                <h3 className="text-lg font-semibold mb-1">No Sleep Recorded</h3>
                <p className="text-muted-foreground text-sm">
                  Track your sleep to monitor your rest and recovery
                </p>
              </div>
              <div className="pt-2">
                <SleepForm dayId={day.id} onSuccess={onUpdate} />
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
