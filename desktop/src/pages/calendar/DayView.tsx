import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { dayService } from '@/services/modules/dayService';
import { MealsSection } from '@/components/day/MealsSection';
import { ExerciseSection } from '@/components/day/ExerciseSection';
import { WaterSection } from '@/components/day/WaterSection';
import { SleepSection } from '@/components/day/SleepSection';
import { MoodSection } from '@/components/day/MoodSection';
import { NotesSection } from '@/components/day/NotesSection';
import { AISummarySection } from '@/components/day/AISummarySection';
import type { Day } from '@/types/models/health';
import {
  Utensils,
  Dumbbell,
  Droplets,
  Moon,
  Smile,
  FileText,
  Sparkles,
  ArrowLeft,
  Loader2,
  Scale,
} from 'lucide-react';

export default function DayView() {
  const { dayId } = useParams<{ dayId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [day, setDay] = useState<Day | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('meals');
  const [weightInput, setWeightInput] = useState<string>('');
  const [isUpdatingWeight, setIsUpdatingWeight] = useState(false);

  const fetchDay = async () => {
    if (!dayId) return;

    try {
      setLoading(true);
      setError(null);
      const data = await dayService.getDay(Number(dayId));
      setDay(data);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to load day data';
      setError(errorMsg);
      toast({
        title: 'Error',
        description: errorMsg,
        variant: 'destructive',
      });
      console.error('Error fetching day:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDay();
  }, [dayId]);

  useEffect(() => {
    if (day?.weight) {
      setWeightInput(day.weight.toString());
    }
  }, [day?.weight]);

  const handleWeightSave = async () => {
    if (!day || !dayId) return;

    const weight = parseFloat(weightInput);
    if (isNaN(weight) || weight <= 0 || weight > 500) {
      toast({
        title: 'Invalid Weight',
        description: 'Please enter a valid weight between 1 and 500 kg',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsUpdatingWeight(true);
      await dayService.updateDay(Number(dayId), { weight });
      setDay({ ...day, weight });
      toast({
        title: 'Success',
        description: 'Weight updated successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update weight',
        variant: 'destructive',
      });
    } finally {
      setIsUpdatingWeight(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !day) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <p className="text-destructive">{error || 'Day not found'}</p>
        <Button onClick={() => navigate('/calendar')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Calendar
        </Button>
      </div>
    );
  }

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const options: Intl.DateTimeFormatOptions = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    };
    return date.toLocaleDateString('en-US', options);
  };

  return (
    <div className="container mx-auto py-6 px-4 max-w-6xl h-full overflow-y-auto">
      {/* Header */}
      <div className="mb-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/calendar')}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Calendar
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">{formatDate(day.date)}</h1>
            {day.tag && (
              <p className="text-muted-foreground mt-1">Tag: {day.tag}</p>
            )}
          </div>
          <div className="flex gap-4 items-end">
            {/* Weight Input */}
            <div className="text-right">
              <p className="text-sm text-muted-foreground mb-1 flex items-center gap-1">
                <Scale className="h-3 w-3" />
                Weight (kg)
              </p>
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  value={weightInput}
                  onChange={(e) => setWeightInput(e.target.value)}
                  onBlur={handleWeightSave}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleWeightSave();
                    }
                  }}
                  placeholder="Enter weight"
                  className="w-28 h-9"
                  step="0.1"
                  min="1"
                  max="500"
                  disabled={isUpdatingWeight}
                />
              </div>
            </div>
            {/* Feeling */}
            {day.feeling && (
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Feeling</p>
                <p className="text-2xl">{'😊'.repeat(day.feeling)}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-7 mb-6">
          <TabsTrigger value="meals" className="flex items-center gap-1">
            <Utensils className="h-4 w-4" />
            <span className="hidden sm:inline">Meals</span>
          </TabsTrigger>
          <TabsTrigger value="exercise" className="flex items-center gap-1">
            <Dumbbell className="h-4 w-4" />
            <span className="hidden sm:inline">Exercise</span>
          </TabsTrigger>
          <TabsTrigger value="water" className="flex items-center gap-1">
            <Droplets className="h-4 w-4" />
            <span className="hidden sm:inline">Water</span>
          </TabsTrigger>
          <TabsTrigger value="sleep" className="flex items-center gap-1">
            <Moon className="h-4 w-4" />
            <span className="hidden sm:inline">Sleep</span>
          </TabsTrigger>
          <TabsTrigger value="mood" className="flex items-center gap-1">
            <Smile className="h-4 w-4" />
            <span className="hidden sm:inline">Mood</span>
          </TabsTrigger>
          <TabsTrigger value="notes" className="flex items-center gap-1">
            <FileText className="h-4 w-4" />
            <span className="hidden sm:inline">Notes</span>
          </TabsTrigger>
          <TabsTrigger value="ai" className="flex items-center gap-1">
            <Sparkles className="h-4 w-4" />
            <span className="hidden sm:inline">AI</span>
          </TabsTrigger>
        </TabsList>

        {/* Meals Tab */}
        <TabsContent value="meals">
          <MealsSection day={day} onUpdate={fetchDay} />
        </TabsContent>

        {/* Exercise Tab */}
        <TabsContent value="exercise">
          <ExerciseSection day={day} onUpdate={fetchDay} />
        </TabsContent>

        {/* Water Tab */}
        <TabsContent value="water">
          <WaterSection day={day} onUpdate={fetchDay} />
        </TabsContent>

        {/* Sleep Tab */}
        <TabsContent value="sleep">
          <SleepSection day={day} onUpdate={fetchDay} />
        </TabsContent>

        {/* Mood Tab */}
        <TabsContent value="mood">
          <MoodSection day={day} onUpdate={fetchDay} />
        </TabsContent>

        {/* Notes Tab */}
        <TabsContent value="notes">
          <NotesSection day={day} onUpdate={fetchDay} />
        </TabsContent>

        {/* AI Summary Tab */}
        <TabsContent value="ai">
          <AISummarySection day={day} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
