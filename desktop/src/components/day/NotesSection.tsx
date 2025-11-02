import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { notesService } from '@/services/modules/notesService';
import { NotesForm } from './NotesForm';
import { DeleteConfirmDialog } from '@/components/ui/DeleteConfirmDialog';
import type { Day } from '@/types/models/health';
import { FileText, Trash2 } from 'lucide-react';

interface NotesSectionProps {
  day: Day;
  onUpdate: () => void;
}

// Simple markdown-like rendering (convert basic markdown to HTML)
const renderMarkdown = (text: string) => {
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];

  lines.forEach((line, index) => {
    if (line.startsWith('# ')) {
      elements.push(
        <h1 key={index} className="text-2xl font-bold mt-4 mb-2">
          {line.substring(2)}
        </h1>
      );
    } else if (line.startsWith('## ')) {
      elements.push(
        <h2 key={index} className="text-xl font-bold mt-3 mb-2">
          {line.substring(3)}
        </h2>
      );
    } else if (line.startsWith('### ')) {
      elements.push(
        <h3 key={index} className="text-lg font-semibold mt-2 mb-1">
          {line.substring(4)}
        </h3>
      );
    } else if (line.startsWith('- ')) {
      elements.push(
        <li key={index} className="ml-4">
          {line.substring(2)}
        </li>
      );
    } else if (line.trim() === '') {
      elements.push(<br key={index} />);
    } else {
      // Handle bold text **text**
      const parts = line.split(/(\*\*.*?\*\*)/g);
      const formatted = parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return (
            <strong key={i} className="font-bold">
              {part.slice(2, -2)}
            </strong>
          );
        }
        return part;
      });
      elements.push(
        <p key={index} className="mb-2">
          {formatted}
        </p>
      );
    }
  });

  return <div className="prose prose-sm max-w-none">{elements}</div>;
};

export function NotesSection({ day, onUpdate }: NotesSectionProps) {
  const { toast } = useToast();
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [noteToDelete, setNoteToDelete] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (noteId: number) => {
    setNoteToDelete(noteId);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!noteToDelete) return;

    try {
      setIsDeleting(true);
      setDeletingId(noteToDelete);
      await notesService.delete(noteToDelete);
      toast({
        title: 'Success',
        description: 'Note deleted successfully',
      });
      onUpdate();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete note',
        variant: 'destructive',
      });
    } finally {
      setIsDeleting(false);
      setDeletingId(null);
      setNoteToDelete(null);
      setDeleteDialogOpen(false);
    }
  };

  const note = day.notes && day.notes.length > 0 ? day.notes[0] : null;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Daily Notes
        </h2>
        {!note && <NotesForm dayId={day.id} onSuccess={onUpdate} />}
      </div>

      {/* Note or Empty State */}
      {note ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>Your Note</span>
              <div className="flex gap-1">
                <NotesForm dayId={day.id} note={note} onSuccess={onUpdate} />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDeleteClick(note.id)}
                  disabled={deletingId === note.id}
                >
                  <Trash2 className="h-4 w-4 text-red-500" />
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-muted/50 p-6 rounded-lg min-h-[200px]">
              {renderMarkdown(note.content)}
            </div>
            <div className="mt-4 text-right">
              <p className="text-xs text-muted-foreground">
                Last updated: {new Date(note.created_at).toLocaleString()}
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-12">
            <div className="text-center space-y-3">
              <FileText className="h-16 w-16 mx-auto text-muted-foreground opacity-50" />
              <div>
                <h3 className="text-lg font-semibold mb-1">No Notes Yet</h3>
                <p className="text-muted-foreground text-sm">
                  Write down your thoughts, achievements, or reflections for the day
                </p>
              </div>
              <div className="pt-2">
                <NotesForm dayId={day.id} onSuccess={onUpdate} />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleConfirmDelete}
        title="Delete Note?"
        description="Are you sure you want to delete this note? This action cannot be undone."
        isDeleting={isDeleting}
      />
    </div>
  );
}
