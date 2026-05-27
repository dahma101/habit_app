import React, { useEffect } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
  TextField,
} from "@mui/material";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { habitSchema, type HabitFormData } from "@/schemas/habit";
import { habitsApi } from "@/api/endpoints/habits";
import { listsApi } from "@/api/endpoints/lists";
import type { Habit } from "@/types";

const PERIODICITIES = [
  { value: "as_many_as_possible", label: "As Many As Possible" },
  { value: "daily", label: "Daily" },
  { value: "twice_weekly", label: "Twice Weekly" },
  { value: "weekly", label: "Weekly" },
  { value: "twice_monthly", label: "Twice Monthly" },
  { value: "monthly", label: "Monthly" },
];

interface Props {
  open: boolean;
  onClose: () => void;
  habit?: Habit | null;
}

export default function HabitModal({ open, onClose, habit }: Props) {
  const queryClient = useQueryClient();
  const isEdit = !!habit;

  const { data: listsData } = useQuery({
    queryKey: ["lists"],
    queryFn: () => listsApi.getAll().then((r) => r.data),
  });

  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<HabitFormData>({
    resolver: zodResolver(habitSchema),
    defaultValues: { title: "", periodicity: "daily", list_id: "" },
  });

  useEffect(() => {
    if (!open) return;
    if (habit) {
      reset({ title: habit.title, periodicity: habit.periodicity, list_id: habit.list_id });
    } else {
      reset({
        title: "",
        periodicity: "daily",
        list_id: listsData?.results[0]?.id ?? "",
      });
    }
  }, [open, habit, listsData, reset]);

  const mutation = useMutation({
    mutationFn: (data: HabitFormData) =>
      isEdit ? habitsApi.update(habit!.id, data) : habitsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["habits"] });
      onClose();
    },
  });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle fontWeight={600}>
        {isEdit ? "Edit Habit" : "New Habit"}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5, mt: 1 }}>
          {mutation.isError && (
            <Alert severity="error">Something went wrong. Please try again.</Alert>
          )}

          <TextField
            label="Habit title"
            {...register("title")}
            error={!!errors.title}
            helperText={errors.title?.message}
            fullWidth
            autoFocus
          />

          <Controller
            name="periodicity"
            control={control}
            render={({ field }) => (
              <FormControl fullWidth error={!!errors.periodicity}>
                <InputLabel>Frequency</InputLabel>
                <Select {...field} label="Frequency">
                  {PERIODICITIES.map((p) => (
                    <MenuItem key={p.value} value={p.value}>
                      {p.label}
                    </MenuItem>
                  ))}
                </Select>
                {errors.periodicity && (
                  <FormHelperText>{errors.periodicity.message}</FormHelperText>
                )}
              </FormControl>
            )}
          />

          <Controller
            name="list_id"
            control={control}
            render={({ field }) => (
              <FormControl fullWidth error={!!errors.list_id}>
                <InputLabel>List</InputLabel>
                <Select {...field} label="List">
                  {listsData?.results.map((l) => (
                    <MenuItem key={l.id} value={l.id}>
                      {l.title}
                    </MenuItem>
                  ))}
                </Select>
                {errors.list_id && (
                  <FormHelperText>{errors.list_id.message}</FormHelperText>
                )}
              </FormControl>
            )}
          />
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={onClose} disabled={mutation.isPending}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit((d) => mutation.mutate(d))}
          variant="contained"
          disabled={mutation.isPending}
          startIcon={mutation.isPending ? <CircularProgress size={16} /> : undefined}
          sx={{ background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)" }}
        >
          {isEdit ? "Save changes" : "Create habit"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
