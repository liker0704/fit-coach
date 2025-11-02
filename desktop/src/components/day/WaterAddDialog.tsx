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
import { useToast } from '@/hooks/use-toast';
import { waterService } from '@/services/modules/waterService';
import { Plus } from 'lucide-react';

const waterSchema = z.object({
  amount: z.number().min(0.1, 'Amount must be at least 0.1L').max(5, 'Amount cannot exceed 5L'),
});

interface WaterAddDialogProps {
  dayId: number;
  onSuccess: () => void;
}

export function WaterAddDialog({ dayId, onSuccess }: WaterAddDialogProps) {
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [amount, setAmount] = useState<number>(0.5);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      // Validate amount
      waterSchema.parse({ amount });
      setLoading(true);

      // Get current time
      const now = new Date();
      const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:00`;

      // Transform empty strings to undefined to prevent 422 validation errors
      await waterService.create(dayId, {
        amount,
        time: time || undefined
      });

      toast({
        title: 'Success',
        description: `Added ${amount}L of water`,
      });

      setOpen(false);
      setAmount(0.5); // Reset to default
      onSuccess();
    } catch (err) {
      if (err instanceof z.ZodError) {
        setError(err.issues[0].message);
      } else {
        toast({
          title: 'Error',
          description: 'Failed to add water intake',
          variant: 'destructive',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Plus className="mr-2 h-4 w-4" />
          Custom Amount
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Add Water Intake</DialogTitle>
          <DialogDescription>
            Enter a custom amount of water consumed
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="amount">Amount (Liters)</Label>
              <Input
                id="amount"
                type="number"
                min="0.1"
                max="5"
                step="0.1"
                value={amount}
                onChange={(e) => {
                  setAmount(Number(e.target.value));
                  setError('');
                }}
                placeholder="e.g., 0.5"
              />
              {error && <p className="text-sm text-red-500">{error}</p>}
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Adding...' : 'Add Water'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
