import { useState, useRef, useEffect } from 'react';
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
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';
import { agentsService, type ChatMessage } from '@/services/modules/agentsService';
import { MessageCircle, Send, Loader2, Bot, User } from 'lucide-react';

interface ChatbotDialogProps {
  triggerButton?: React.ReactNode;
}

export function ChatbotDialog({ triggerButton }: ChatbotDialogProps) {
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Reset conversation when dialog closes
  useEffect(() => {
    if (!open) {
      setMessages([]);
      setInput('');
    }
  }, [open]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await agentsService.chat({
        message: userMessage.content,
        conversation_history: messages,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      toast({
        title: 'Error',
        description: 'Failed to get response. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {triggerButton || (
          <Button variant="outline" size="sm">
            <MessageCircle className="mr-2 h-4 w-4" />
            Chat with AI Coach
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>AI Fitness Coach</DialogTitle>
          <DialogDescription>
            Ask me anything about fitness, nutrition, or your health goals!
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="flex-1 h-[400px] pr-4" ref={scrollRef}>
          <div className="space-y-4">
            {messages.length === 0 && (
              <Card className="p-4 bg-muted">
                <div className="flex items-start gap-3">
                  <Bot className="h-5 w-5 mt-0.5 text-primary" />
                  <div className="flex-1">
                    <p className="text-sm text-muted-foreground">
                      Hi! I'm your AI fitness coach. I can help you with:
                    </p>
                    <ul className="text-sm text-muted-foreground mt-2 space-y-1 list-disc list-inside">
                      <li>Fitness and workout advice</li>
                      <li>Nutrition and meal planning</li>
                      <li>Progress tracking and motivation</li>
                      <li>General health questions</li>
                    </ul>
                  </div>
                </div>
              </Card>
            )}

            {messages.map((message, index) => (
              <Card
                key={index}
                className={`p-4 ${
                  message.role === 'user' ? 'bg-primary/5' : 'bg-muted'
                }`}
              >
                <div className="flex items-start gap-3">
                  {message.role === 'user' ? (
                    <User className="h-5 w-5 mt-0.5" />
                  ) : (
                    <Bot className="h-5 w-5 mt-0.5 text-primary" />
                  )}
                  <div className="flex-1">
                    <p className="text-sm font-medium mb-1">
                      {message.role === 'user' ? 'You' : 'AI Coach'}
                    </p>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              </Card>
            ))}

            {loading && (
              <Card className="p-4 bg-muted">
                <div className="flex items-start gap-3">
                  <Bot className="h-5 w-5 mt-0.5 text-primary" />
                  <div className="flex-1">
                    <p className="text-sm font-medium mb-1">AI Coach</p>
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <p className="text-sm text-muted-foreground">Thinking...</p>
                    </div>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </ScrollArea>

        <div className="flex gap-2 pt-4 border-t">
          <Input
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
            className="flex-1"
          />
          <Button onClick={handleSend} disabled={!input.trim() || loading}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
