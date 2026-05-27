import React from "react";
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from "@mui/material";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import type { Habit } from "@/types";

interface Props {
  open: boolean;
  habit: Habit | null;
  onConfirm: () => void;
  onClose: () => void;
  loading: boolean;
  error: string | null;
}

export default function CheckInModal({ open, habit, onConfirm, onClose, loading, error }: Props) {
  if (!habit) return null;

  const dueLabel = habit.due_to
    ? new Date(habit.due_to).toLocaleDateString(undefined, {
        weekday: "short",
        month: "short",
        day: "numeric",
      })
    : "no due date";

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ fontWeight: 700 }}>Confirm check-in</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <Typography variant="body1" mb={1}>
          Mark <strong>{habit.title}</strong> as done?
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Due by {dueLabel}
        </Typography>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
        <Button onClick={onClose} disabled={loading} variant="outlined" color="inherit">
          Cancel
        </Button>
        <Button
          onClick={onConfirm}
          disabled={loading}
          variant="contained"
          startIcon={<CheckCircleOutlineIcon />}
          sx={{
            background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
          }}
        >
          {loading ? "Checking in…" : "Check In"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
