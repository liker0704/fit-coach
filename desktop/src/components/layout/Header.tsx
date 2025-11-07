import { useLocation } from 'react-router-dom';
import { Moon, Sun, User as UserIcon, MessageCircle, Apple, Dumbbell } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { useStore } from '@/store';
import { useShallow } from 'zustand/react/shallow';
import { ChatbotDialog, CoachDialog } from '@/components/agents';

const pageNames: Record<string, string> = {
  '/': 'Calendar',
  '/stats': 'Statistics',
  '/profile': 'Profile',
};

export default function Header() {
  const location = useLocation();
  const { user, logout } = useStore(
    useShallow(state => ({ user: state.user, logout: state.logout }))
  );

  // Get page title from pathname or default to "Dashboard"
  const getPageTitle = () => {
    // For dynamic routes like /day/:id, extract the base path
    const basePath = location.pathname.split('/').slice(0, 2).join('/');

    if (basePath.startsWith('/day')) {
      return 'Day View';
    }

    return pageNames[location.pathname] || 'Dashboard';
  };

  return (
    <header className="h-16 border-b border-border bg-card px-6 flex items-center justify-between">
      {/* Page Title */}
      <h2 className="text-xl font-semibold">{getPageTitle()}</h2>

      {/* Right Section */}
      <div className="flex items-center gap-2">
        {/* AI Agents */}
        <ChatbotDialog
          triggerButton={
            <Button variant="ghost" size="sm" className="gap-2">
              <MessageCircle className="h-4 w-4" />
              <span className="hidden md:inline">AI Chat</span>
            </Button>
          }
        />

        <CoachDialog
          type="nutrition"
          triggerButton={
            <Button variant="ghost" size="sm" className="gap-2">
              <Apple className="h-4 w-4" />
              <span className="hidden md:inline">Nutrition</span>
            </Button>
          }
        />

        <CoachDialog
          type="workout"
          triggerButton={
            <Button variant="ghost" size="sm" className="gap-2">
              <Dumbbell className="h-4 w-4" />
              <span className="hidden md:inline">Workout</span>
            </Button>
          }
        />

        {/* Dark Mode Toggle Placeholder */}
        <Button variant="ghost" size="icon" className="relative ml-2">
          <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>

        {/* User Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="rounded-full">
              <UserIcon className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">
                  {user?.full_name || 'User'}
                </p>
                <p className="text-xs leading-none text-muted-foreground">
                  {user?.email}
                </p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout} className="text-destructive">
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
