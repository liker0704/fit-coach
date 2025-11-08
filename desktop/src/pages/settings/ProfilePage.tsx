import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useStore } from '@/store';
import { useShallow } from 'zustand/react/shallow';
import { userService } from '@/services/modules/userService';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { TimePicker24 } from '@/components/ui/TimePicker24';
import { Sun, Moon, Monitor } from 'lucide-react';

interface FormData {
  full_name: string;
  age: number;
  height: number;
  weight: number;
  target_weight: number;
  water_goal: number;
  calorie_goal: number;
  sleep_goal: number;
  language: string;
  notifications_enabled: boolean;
  reminder_time: string;
}

export default function ProfilePage() {
  const { t, i18n } = useTranslation();
  const { user, logout, setUser } = useStore(
    useShallow(state => ({ user: state.user, logout: state.logout, setUser: state.setUser }))
  );
  const { theme, setTheme } = useStore(
    useShallow(state => ({ theme: state.theme, setTheme: state.setTheme }))
  );
  const navigate = useNavigate();
  const { toast } = useToast();

  const [formData, setFormData] = useState<FormData>({
    full_name: user?.full_name || '',
    age: user?.age || 30,
    height: user?.height || 180,
    weight: user?.weight || 75,
    target_weight: user?.target_weight || 70,
    water_goal: user?.water_goal || 2.5,
    calorie_goal: user?.calorie_goal || 2000,
    sleep_goal: user?.sleep_goal || 7.5,
    language: i18n.language || 'en',
    notifications_enabled: false,
    reminder_time: '21:00',
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        full_name: user.full_name || '',
        age: user.age || 30,
        height: user.height || 180,
        weight: user.weight || 75,
        target_weight: user.target_weight || 70,
        water_goal: user.water_goal || 2.5,
        calorie_goal: user.calorie_goal || 2000,
        sleep_goal: user.sleep_goal || 7.5,
      }));
    }
  }, [user]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.full_name || formData.full_name.length < 2) {
      newErrors.full_name = 'Full name must be at least 2 characters';
    }

    if (formData.age < 1 || formData.age > 120) {
      newErrors.age = 'Age must be between 1 and 120';
    }

    if (formData.height < 50 || formData.height > 250) {
      newErrors.height = 'Height must be between 50 and 250 cm';
    }

    if (formData.weight < 30 || formData.weight > 300) {
      newErrors.weight = 'Weight must be between 30 and 300 kg';
    }

    if (formData.target_weight < 30 || formData.target_weight > 300) {
      newErrors.target_weight = 'Target weight must be between 30 and 300 kg';
    }

    if (formData.water_goal < 0.5 || formData.water_goal > 10) {
      newErrors.water_goal = 'Water goal must be between 0.5 and 10 L';
    }

    if (formData.calorie_goal < 500 || formData.calorie_goal > 5000) {
      newErrors.calorie_goal = 'Calorie goal must be between 500 and 5000 kcal';
    }

    if (formData.sleep_goal < 1 || formData.sleep_goal > 15) {
      newErrors.sleep_goal = 'Sleep goal must be between 1 and 15 hours';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      toast({
        title: 'Validation Error',
        description: 'Please check the form for errors',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      const updatedUser = await userService.updateProfile({
        full_name: formData.full_name,
        age: formData.age,
        height: formData.height,
        weight: formData.weight,
        target_weight: formData.target_weight,
        water_goal: formData.water_goal,
        calorie_goal: formData.calorie_goal,
        sleep_goal: formData.sleep_goal,
      });

      setUser(updatedUser);

      toast({
        title: 'Success',
        description: 'Profile updated successfully',
      });
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast({
        title: 'Error',
        description: 'Failed to update profile. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleInputChange = (field: keyof FormData, value: string | number | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));

    // Handle language change
    if (field === 'language' && typeof value === 'string') {
      i18n.changeLanguage(value);
      toast({
        title: 'Language Changed',
        description: 'Language has been updated successfully',
      });
    }

    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  return (
    <div className="container max-w-2xl mx-auto p-6 h-full overflow-y-auto">
      <h1 className="text-3xl font-bold mb-6">{t('profile.personalInfo')}</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Personal Information */}
        <Card>
          <CardHeader>
            <CardTitle>{t('profile.personalInfo')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="full_name">{t('auth.fullName')}</Label>
              <Input
                id="full_name"
                value={formData.full_name}
                onChange={(e) => handleInputChange('full_name', e.target.value)}
                className={errors.full_name ? 'border-red-500' : ''}
              />
              {errors.full_name && (
                <p className="text-sm text-red-500 mt-1">{errors.full_name}</p>
              )}
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                value={user?.email || ''}
                disabled
                className="bg-gray-100 dark:bg-gray-800 cursor-not-allowed"
              />
              <p className="text-sm text-gray-500 mt-1">Email cannot be changed</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="age">Age (years)</Label>
                <Input
                  id="age"
                  type="number"
                  min="1"
                  max="120"
                  step="1"
                  value={formData.age}
                  onChange={(e) => handleInputChange('age', parseInt(e.target.value) || 0)}
                  className={errors.age ? 'border-red-500' : ''}
                />
                {errors.age && (
                  <p className="text-sm text-red-500 mt-1">{errors.age}</p>
                )}
              </div>

              <div>
                <Label htmlFor="height">Height (cm)</Label>
                <Input
                  id="height"
                  type="number"
                  min="50"
                  max="250"
                  step="1"
                  value={formData.height}
                  onChange={(e) => handleInputChange('height', parseInt(e.target.value) || 0)}
                  className={errors.height ? 'border-red-500' : ''}
                />
                {errors.height && (
                  <p className="text-sm text-red-500 mt-1">{errors.height}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="weight">Current Weight (kg)</Label>
                <Input
                  id="weight"
                  type="number"
                  min="30"
                  max="300"
                  step="0.1"
                  value={formData.weight}
                  onChange={(e) => handleInputChange('weight', parseFloat(e.target.value) || 0)}
                  className={errors.weight ? 'border-red-500' : ''}
                />
                {errors.weight && (
                  <p className="text-sm text-red-500 mt-1">{errors.weight}</p>
                )}
              </div>

              <div>
                <Label htmlFor="target_weight">Target Weight (kg)</Label>
                <Input
                  id="target_weight"
                  type="number"
                  min="30"
                  max="300"
                  step="0.1"
                  value={formData.target_weight}
                  onChange={(e) => handleInputChange('target_weight', parseFloat(e.target.value) || 0)}
                  className={errors.target_weight ? 'border-red-500' : ''}
                />
                {errors.target_weight && (
                  <p className="text-sm text-red-500 mt-1">{errors.target_weight}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Health Goals */}
        <Card>
          <CardHeader>
            <CardTitle>{t('profile.healthGoals')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="water_goal">{t('profile.waterGoal')}</Label>
              <Input
                id="water_goal"
                type="number"
                min="0.5"
                max="10"
                step="0.1"
                value={formData.water_goal}
                onChange={(e) => handleInputChange('water_goal', parseFloat(e.target.value) || 0)}
                className={errors.water_goal ? 'border-red-500' : ''}
              />
              {errors.water_goal && (
                <p className="text-sm text-red-500 mt-1">{errors.water_goal}</p>
              )}
            </div>

            <div>
              <Label htmlFor="calorie_goal">Daily Calorie Goal (kcal)</Label>
              <Input
                id="calorie_goal"
                type="number"
                min="500"
                max="5000"
                step="1"
                value={formData.calorie_goal}
                onChange={(e) => handleInputChange('calorie_goal', parseInt(e.target.value) || 0)}
                className={errors.calorie_goal ? 'border-red-500' : ''}
              />
              {errors.calorie_goal && (
                <p className="text-sm text-red-500 mt-1">{errors.calorie_goal}</p>
              )}
            </div>

            <div>
              <Label htmlFor="sleep_goal">Sleep Goal (hours)</Label>
              <Input
                id="sleep_goal"
                type="number"
                min="1"
                max="15"
                step="0.1"
                value={formData.sleep_goal}
                onChange={(e) => handleInputChange('sleep_goal', parseFloat(e.target.value) || 0)}
                className={errors.sleep_goal ? 'border-red-500' : ''}
              />
              {errors.sleep_goal && (
                <p className="text-sm text-red-500 mt-1">{errors.sleep_goal}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* App Settings */}
        <Card>
          <CardHeader>
            <CardTitle>{t('profile.appSettings')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>{t('profile.theme')}</Label>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant={theme === 'light' ? 'default' : 'outline'}
                  onClick={() => setTheme('light')}
                  className="flex-1"
                >
                  <Sun className="mr-2 h-4 w-4" />
                  Light
                </Button>
                <Button
                  type="button"
                  variant={theme === 'dark' ? 'default' : 'outline'}
                  onClick={() => setTheme('dark')}
                  className="flex-1"
                >
                  <Moon className="mr-2 h-4 w-4" />
                  Dark
                </Button>
                <Button
                  type="button"
                  variant={theme === 'system' ? 'default' : 'outline'}
                  onClick={() => setTheme('system')}
                  className="flex-1"
                >
                  <Monitor className="mr-2 h-4 w-4" />
                  System
                </Button>
              </div>
              <p className="text-sm text-gray-500">Theme changes apply instantly</p>
            </div>

            <div>
              <Label htmlFor="language">{t('profile.language')}</Label>
              <Select
                value={formData.language}
                onValueChange={(value) => handleInputChange('language', value)}
              >
                <SelectTrigger id="language">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="ru">Русский</SelectItem>
                  <SelectItem value="cz">Čeština</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-sm text-gray-500 mt-1">Language changes apply instantly</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t('profile.dailyReminder')}</Label>
                  <p className="text-sm text-gray-500">
                    Get reminded to log your day
                  </p>
                </div>
                <Checkbox
                  checked={formData.notifications_enabled}
                  onCheckedChange={(checked) =>
                    handleInputChange('notifications_enabled', !!checked)
                  }
                />
              </div>

              {formData.notifications_enabled && (
                <div className="ml-6">
                  <TimePicker24
                    label="Reminder Time"
                    value={formData.reminder_time}
                    onChange={(value) => handleInputChange('reminder_time', value)}
                    placeholder="21:00"
                    className="w-40"
                  />
                </div>
              )}
              <p className="text-sm text-gray-500">Notifications will be implemented in future</p>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex gap-4">
          <Button type="submit" disabled={loading} className="flex-1">
            {loading ? t('common.loading') : t('common.save')}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={handleLogout}
            className="flex-1"
          >
            {t('auth.logout')}
          </Button>
        </div>
      </form>
    </div>
  );
}
