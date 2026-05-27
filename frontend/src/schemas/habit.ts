import { z } from "zod";

export const habitSchema = z.object({
  title: z.string().min(1, "Title is required").max(500),
  periodicity: z.enum([
    "as_many_as_possible",
    "daily",
    "twice_weekly",
    "weekly",
    "twice_monthly",
    "monthly",
  ]),
  list_id: z.string().uuid("Invalid list"),
});

export type HabitFormData = z.infer<typeof habitSchema>;
