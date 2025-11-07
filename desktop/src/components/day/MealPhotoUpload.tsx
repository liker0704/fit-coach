import { useState, useCallback, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { mealsService } from '@/services/modules/mealsService';
import type { MealProcessingStatus, RecognizedItem } from '@/services/modules/mealsService';
import { Camera, Upload, X, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

interface MealPhotoUploadProps {
  dayId: number;
  onSuccess: () => void;
}

export function MealPhotoUpload({ dayId, onSuccess }: MealPhotoUploadProps) {
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<MealProcessingStatus | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [category, setCategory] = useState<'breakfast' | 'lunch' | 'dinner' | 'snack'>('lunch');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Clean up polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  // Poll for processing status
  const startPolling = useCallback((mealId: number) => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    const poll = async () => {
      try {
        const status = await mealsService.getProcessingStatus(mealId);
        setProcessingStatus(status);

        if (status.status === 'completed') {
          setProcessing(false);
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
          }
          toast({
            title: 'Success!',
            description: 'Meal photo processed successfully',
          });
          onSuccess();
          setTimeout(() => setOpen(false), 2000);
        } else if (status.status === 'failed') {
          setProcessing(false);
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
          }
          toast({
            title: 'Processing Failed',
            description: status.error || 'Failed to process meal photo',
            variant: 'destructive',
          });
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    };

    // Initial poll
    poll();

    // Poll every 2.5 seconds
    pollingIntervalRef.current = setInterval(poll, 2500);
  }, [onSuccess, toast]);

  // Handle drag events
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  // Handle drop
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      handleFileSelect(file);
    } else {
      toast({
        title: 'Invalid file',
        description: 'Please upload an image file (PNG, JPG, JPEG)',
        variant: 'destructive',
      });
    }
  }, [toast]);

  // Handle file selection
  const handleFileSelect = useCallback((file: File) => {
    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: 'File too large',
        description: 'File size must be less than 10MB',
        variant: 'destructive',
      });
      return;
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast({
        title: 'Invalid file type',
        description: 'Please upload an image file (PNG, JPG, JPEG)',
        variant: 'destructive',
      });
      return;
    }

    setSelectedFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result as string);
    };
    reader.readAsDataURL(file);
  }, [toast]);

  // Handle file input change
  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  }, [handleFileSelect]);

  // Handle upload
  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setUploading(true);

      // Upload photo
      const response = await mealsService.uploadPhoto(dayId, category, selectedFile);

      toast({
        title: 'Photo uploaded',
        description: 'Processing with AI Vision...',
      });

      setUploading(false);
      setProcessing(true);

      // Start polling for status
      startPolling(response.meal_id);
    } catch (error: any) {
      console.error('Upload error:', error);
      toast({
        title: 'Upload failed',
        description: error?.response?.data?.detail || 'Failed to upload photo',
        variant: 'destructive',
      });
      setUploading(false);
    }
  };

  // Reset state
  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setProcessingStatus(null);
    setUploading(false);
    setProcessing(false);
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }
  };

  // Handle dialog close
  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      handleReset();
    }
    setOpen(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Camera className="mr-2 h-4 w-4" />
          Add Meal Photo
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Upload Meal Photo</DialogTitle>
          <DialogDescription>
            Take a photo of your meal and let AI recognize the food and calculate nutrition automatically
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Category Selection */}
          <div className="space-y-2">
            <Label htmlFor="category">Meal Category</Label>
            <Select value={category} onValueChange={(value: any) => setCategory(value)}>
              <SelectTrigger id="category">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="breakfast">Breakfast</SelectItem>
                <SelectItem value="lunch">Lunch</SelectItem>
                <SelectItem value="dinner">Dinner</SelectItem>
                <SelectItem value="snack">Snack</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* File Upload Area */}
          {!selectedFile && !processing && (
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                dragActive
                  ? 'border-primary bg-primary/5'
                  : 'border-gray-300 hover:border-primary/50'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleFileInputChange}
              />
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-sm text-gray-600 mb-2">
                Drag and drop your meal photo here, or click to browse
              </p>
              <p className="text-xs text-gray-400">
                Supports: PNG, JPG, JPEG (max 10MB)
              </p>
            </div>
          )}

          {/* Preview */}
          {selectedFile && !processing && (
            <Card>
              <CardContent className="p-4">
                <div className="relative">
                  {previewUrl && (
                    <img
                      src={previewUrl}
                      alt="Preview"
                      className="w-full h-64 object-cover rounded-lg"
                    />
                  )}
                  <Button
                    variant="destructive"
                    size="icon"
                    className="absolute top-2 right-2"
                    onClick={handleReset}
                    disabled={uploading}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                <div className="mt-4 space-y-2">
                  <p className="text-sm font-medium">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Processing Status */}
          {processing && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {processingStatus?.status === 'completed' ? (
                    <>
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                      <span>Processing Complete!</span>
                    </>
                  ) : processingStatus?.status === 'failed' ? (
                    <>
                      <AlertCircle className="h-5 w-5 text-red-500" />
                      <span>Processing Failed</span>
                    </>
                  ) : (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Processing with AI Vision...</span>
                    </>
                  )}
                </CardTitle>
                <CardDescription>
                  {processingStatus?.status === 'completed'
                    ? 'Meal recognized and nutrition calculated'
                    : processingStatus?.status === 'failed'
                    ? processingStatus.error
                    : 'Recognizing food items and calculating nutrition'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {processingStatus?.status === 'processing' && (
                  <Progress value={undefined} className="w-full" />
                )}

                {/* Recognized Items */}
                {processingStatus?.recognized_items && processingStatus.recognized_items.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <Label>Recognized Items:</Label>
                    <div className="space-y-2">
                      {processingStatus.recognized_items.map((item: RecognizedItem, index: number) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                        >
                          <div>
                            <p className="text-sm font-medium">{item.name}</p>
                            <p className="text-xs text-gray-500">
                              {item.quantity} {item.unit}
                              {item.preparation && ` (${item.preparation})`}
                            </p>
                          </div>
                          <span
                            className={`text-xs px-2 py-1 rounded ${
                              item.confidence === 'high'
                                ? 'bg-green-100 text-green-700'
                                : item.confidence === 'medium'
                                ? 'bg-yellow-100 text-yellow-700'
                                : 'bg-red-100 text-red-700'
                            }`}
                          >
                            {item.confidence}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Meal Data */}
                {processingStatus?.meal_data && (
                  <div className="mt-4 p-4 bg-green-50 rounded-lg">
                    <h4 className="font-medium text-green-900 mb-2">Nutrition Summary</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-gray-600">Calories:</span>{' '}
                        <span className="font-medium">{processingStatus.meal_data.calories} kcal</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Protein:</span>{' '}
                        <span className="font-medium">{processingStatus.meal_data.protein}g</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Carbs:</span>{' '}
                        <span className="font-medium">{processingStatus.meal_data.carbs}g</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Fat:</span>{' '}
                        <span className="font-medium">{processingStatus.meal_data.fat}g</span>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Upload Button */}
          {selectedFile && !processing && (
            <Button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full"
            >
              {uploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload & Process
                </>
              )}
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
