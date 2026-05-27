export interface User {
  id: string;
  full_name: string;
  email: string;
  avatar: string;
  created_at: string;
}

export type Periodicity =
  | "as_many_as_possible"
  | "daily"
  | "twice_weekly"
  | "weekly"
  | "twice_monthly"
  | "monthly";

export interface HabitList {
  id: string;
  title: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface Habit {
  id: string;
  title: string;
  periodicity: Periodicity;
  list_id: string;
  list_title: string | null;
  last_check_time: string | null;
  is_checked: boolean;
  due_from: string | null;
  due_to: string | null;
  streak_count: number;
  created_at: string;
  updated_at: string;
}

export interface HabitLog {
  id: string;
  habit_id: string;
  list_id: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse extends AuthTokens {
  user: User;
}

export interface GeneralReport {
  tracked_habits: Habit[];
  habits_by_periodicity: Record<string, Habit[]>;
  longest_streak: number;
  least_tracked_habit: Habit | null;
}

export interface HabitHistoryReport {
  habit_id: string;
  title: string;
  streak_count: number;
  longest_streak: number;
  log_history: { id: string; checked_at: string }[];
}
