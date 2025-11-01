import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { aiService } from '@/services/modules/aiService';
import type { Day } from '@/types/models/health';
import { Sparkles, Loader2, RefreshCw } from 'lucide-react';

interface AISummarySectionProps {
  day: Day;
}

// Render stars for effort score
const renderStars = (score: number) => {
  const normalizedScore = Math.round((score / 10) * 5); // Convert 0-10 to 0-5
  return Array.from({ length: 5 }, (_, i) => (
    <span key={i} className="text-xl">
      {i < normalizedScore ? '⭐' : '☆'}
    </span>
  ));
};

export function AISummarySection({ day }: AISummarySectionProps) {
  const { toast } = useToast();
  const [summary, setSummary] = useState<string>(day.summary || '');
  const [loading, setLoading] = useState(false);

  const generateSummary = async () => {
    setLoading(true);
    try {
      const result = await aiService.generateSummary(day.id);
      setSummary(result);
      toast({
        title: 'Success',
        description: 'AI summary generated successfully',
      });
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || 'Failed to generate summary';
      toast({
        title: 'Error',
        description: errorMessage.includes('LLM')
          ? 'AI service not configured. Please set up LLM configuration.'
          : errorMessage,
        variant: 'destructive',
      });
      console.error('AI summary error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-purple-500" />
          AI Summary
        </h2>
        {summary && !loading && (
          <Button
            variant="outline"
            size="sm"
            onClick={generateSummary}
            disabled={loading}
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Regenerate
          </Button>
        )}
      </div>

      {/* Effort Score Card (if available) */}
      {day.effort_score !== null && day.effort_score !== undefined && (
        <Card className="border-purple-200 bg-purple-50/50 dark:bg-purple-950/20">
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-2">Effort Score</p>
              <div className="flex items-center justify-center gap-2 mb-2">
                <span className="text-4xl font-bold text-purple-600 dark:text-purple-400">
                  {day.effort_score}
                </span>
                <span className="text-2xl text-muted-foreground">/10</span>
              </div>
              <div className="flex items-center justify-center gap-1">
                {renderStars(day.effort_score)}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-purple-500" />
            Daily Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="py-12 text-center">
              <Loader2 className="h-12 w-12 mx-auto mb-4 animate-spin text-purple-500" />
              <p className="text-sm text-muted-foreground">
                Analyzing your day with AI...
              </p>
            </div>
          ) : summary ? (
            <div className="space-y-4">
              <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 p-6 rounded-lg border border-purple-200 dark:border-purple-800">
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <p className="text-base leading-relaxed whitespace-pre-wrap">
                    {summary}
                  </p>
                </div>
              </div>

              {/* LLM Advice (if available) */}
              {day.llm_advice && (
                <div className="bg-blue-50 dark:bg-blue-950/30 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">💡</div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold mb-1 text-blue-900 dark:text-blue-100">
                        Micro-step for tomorrow:
                      </p>
                      <p className="text-sm text-blue-800 dark:text-blue-200">
                        {day.llm_advice}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="py-12 text-center space-y-4">
              <div className="text-6xl mb-4">🤖</div>
              <div>
                <h3 className="text-lg font-semibold mb-2">No Summary Yet</h3>
                <p className="text-muted-foreground text-sm mb-4">
                  Generate an AI-powered summary of your day's activities, nutrition, and
                  progress
                </p>
              </div>
              <Button onClick={generateSummary} disabled={loading} size="lg">
                <Sparkles className="mr-2 h-5 w-5" />
                Generate AI Summary
              </Button>
              <p className="text-xs text-muted-foreground mt-4">
                Note: This feature requires LLM configuration in the backend
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
