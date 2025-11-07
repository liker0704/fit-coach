import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { agentsService } from '@/services/modules/agentsService';
import { Loader2, Apple, Dumbbell } from 'lucide-react';

interface CoachDialogProps {
  type: 'nutrition' | 'workout';
  triggerButton?: React.ReactNode;
}

export function CoachDialog({ type, triggerButton }: CoachDialogProps) {
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const isNutrition = type === 'nutrition';
  const icon = isNutrition ? Apple : Dumbbell;
  const Icon = icon;
  const title = isNutrition ? 'Nutrition Coach' : 'Workout Coach';
  const description = isNutrition
    ? 'Get personalized nutrition advice based on your goals and progress'
    : 'Get personalized workout coaching and training advice';
  const placeholder = isNutrition
    ? 'Ask about meal planning, macros, nutrition timing, etc.'
    : 'Ask about exercises, training programs, form tips, etc.';

  const handleSubmit = async () => {
    if (!question.trim() || loading) return;

    setLoading(true);
    setResponse(null);

    try {
      const result = isNutrition
        ? await agentsService.getNutritionCoaching({ message: question })
        : await agentsService.getWorkoutCoaching({ message: question });

      setResponse(result.response);
    } catch (error) {
      console.error('Coach error:', error);
      toast({
        title: 'Error',
        description: 'Failed to get coaching advice. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setQuestion('');
    setResponse(null);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {triggerButton || (
          <Button variant="outline" size="sm">
            <Icon className="mr-2 h-4 w-4" />
            {title}
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Icon className="h-5 w-5" />
            {title}
          </DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>

        <div className="flex-1 space-y-4 overflow-y-auto">
          {/* Question Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Your Question</label>
            <Textarea
              placeholder={placeholder}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={loading}
              rows={4}
              className="resize-none"
            />
          </div>

          {/* Response */}
          {response && (
            <Card className="p-4 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 border-purple-200 dark:border-purple-800">
              <div className="flex items-start gap-3">
                <Icon className="h-5 w-5 mt-1 text-primary flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-semibold mb-2">Coach's Advice:</p>
                  <div className="prose prose-sm max-w-none dark:prose-invert">
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">
                      {response}
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          )}

          {/* Loading State */}
          {loading && (
            <Card className="p-8 bg-muted">
              <div className="flex flex-col items-center justify-center text-center space-y-4">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <p className="text-sm text-muted-foreground">
                  Analyzing your data and generating personalized advice...
                </p>
              </div>
            </Card>
          )}

          {/* Tips */}
          {!response && !loading && (
            <Card className="p-4 bg-muted border-dashed">
              <div className="text-sm text-muted-foreground">
                <p className="font-semibold mb-2">💡 Tips:</p>
                <ul className="space-y-1 list-disc list-inside">
                  {isNutrition ? (
                    <>
                      <li>Ask about meal planning and timing</li>
                      <li>Get advice on hitting your macro goals</li>
                      <li>Learn about nutrition for your fitness goals</li>
                      <li>Understand portion sizes and food choices</li>
                    </>
                  ) : (
                    <>
                      <li>Get workout program recommendations</li>
                      <li>Learn proper exercise form and technique</li>
                      <li>Ask about progressive overload strategies</li>
                      <li>Get advice on recovery and rest days</li>
                    </>
                  )}
                </ul>
              </div>
            </Card>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-4 border-t">
          {response ? (
            <>
              <Button onClick={handleReset} variant="outline" className="flex-1">
                Ask Another Question
              </Button>
              <Button onClick={() => setOpen(false)}>Done</Button>
            </>
          ) : (
            <>
              <Button
                onClick={handleSubmit}
                disabled={!question.trim() || loading}
                className="flex-1"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Getting Advice...
                  </>
                ) : (
                  <>
                    <Icon className="mr-2 h-4 w-4" />
                    Get Coaching
                  </>
                )}
              </Button>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
