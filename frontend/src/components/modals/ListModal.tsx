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
  TextField,
} from "@mui/material";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { listSchema, type ListFormData } from "@/schemas/list";
import { listsApi } from "@/api/endpoints/lists";
import type { HabitList } from "@/types";

interface Props {
  open: boolean;
  onClose: () => void;
  list?: HabitList | null;
}

export default function ListModal({ open, onClose, list }: Props) {
  const queryClient = useQueryClient();
  const isEdit = !!list;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ListFormData>({
    resolver: zodResolver(listSchema),
    defaultValues: { title: "" },
  });

  useEffect(() => {
    if (open) reset({ title: list?.title ?? "" });
  }, [open, list, reset]);

  const mutation = useMutation({
    mutationFn: (data: ListFormData) =>
      isEdit ? listsApi.update(list!.id, data) : listsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lists"] });
      onClose();
    },
  });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle fontWeight={600}>{isEdit ? "Edit List" : "New List"}</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 1 }}>
          {mutation.isError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Something went wrong. Please try again.
            </Alert>
          )}
          <TextField
            label="List name"
            {...register("title")}
            error={!!errors.title}
            helperText={errors.title?.message}
            fullWidth
            autoFocus
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
          {isEdit ? "Save changes" : "Create list"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
