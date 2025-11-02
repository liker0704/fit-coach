import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

interface TimePicker24Props {
  value?: string;
  onChange: (value: string) => void;
  label?: string;
  placeholder?: string;
  required?: boolean;
  className?: string;
  disabled?: boolean;
}

export function TimePicker24({
  value = '',
  onChange,
  label,
  placeholder = 'HH:MM',
  required = false,
  className,
  disabled = false,
}: TimePicker24Props) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;

    // Allow empty value
    if (!inputValue) {
      onChange('');
      return;
    }

    // Validate and format time input
    // The native input type="time" already handles validation
    onChange(inputValue);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;

    if (!inputValue) {
      onChange('');
      return;
    }

    // Ensure proper HH:MM format
    const parts = inputValue.split(':');
    if (parts.length === 2) {
      const hours = parseInt(parts[0], 10);
      const minutes = parseInt(parts[1], 10);

      if (!isNaN(hours) && !isNaN(minutes) && hours >= 0 && hours < 24 && minutes >= 0 && minutes < 60) {
        const formatted = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
        onChange(formatted);
      }
    }
  };

  return (
    <div className={cn('grid gap-2', className)}>
      {label && (
        <Label htmlFor="time-input">
          {label}
          {required && <span className="text-destructive ml-1">*</span>}
        </Label>
      )}
      <Input
        id="time-input"
        type="time"
        value={value}
        onChange={handleChange}
        onBlur={handleBlur}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        className="w-full"
        step="60"
      />
    </div>
  );
}
