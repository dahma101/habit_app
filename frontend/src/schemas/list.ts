import { z } from "zod";

export const listSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(255)
    .refine((v) => v.trim().toLowerCase() !== "default", {
      message: "'Default' is a reserved name",
    }),
});

export type ListFormData = z.infer<typeof listSchema>;
