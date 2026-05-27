import React, { useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Fab,
  IconButton,
  Tooltip,
  Typography,
  Zoom,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import LocalFireDepartmentIcon from "@mui/icons-material/LocalFireDepartment";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { habitsApi } from "@/api/endpoints/habits";
import HabitModal from "@/components/modals/HabitModal";
import ConfirmDialog from "@/components/modals/ConfirmDialog";
import CheckInModal from "@/components/modals/CheckInModal";
import type { Habit } from "@/types";

const PERIODICITY_COLORS: Record<string, "primary" | "secondary" | "success" | "warning" | "info"> = {
  as_many_as_possible: "info",
  daily: "primary",
  twice_weekly: "secondary",
  weekly: "success",
  twice_monthly: "warning",
  monthly: "info",
};

function extractCheckInError(err: unknown): string | null {
  if (!err) return null;
  let raw = "Check-in failed. Please try again.";
  if (err && typeof err === "object" && "response" in err) {
    const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
    if (detail) raw = detail;
  } else if (err instanceof Error) {
    raw = err.message;
  }
  if (raw.toLowerCase().includes("outside the current due window")) {
    return "Too early to check-in this habit.";
  }
  return raw;
}

function getStatusInfo(habit: Habit): { label: string; color: "success" | "warning" | "error" | "default" } {
  if (habit.is_checked) return { label: "Done ✓", color: "success" };
  if (!habit.due_to) return { label: "No due date", color: "default" };
  const now = Date.now();
  const dueTo = new Date(habit.due_to).getTime();
  if (now > dueTo) return { label: "Overdue", color: "error" };
  const daysLeft = Math.ceil((dueTo - now) / 86400000);
  if (daysLeft <= 1) return { label: "Due today", color: "warning" };
  return { label: `Due in ${daysLeft}d`, color: "default" };
}

function sortHabitsByDue(habits: Habit[]): Habit[] {
  return [...habits].sort((a, b) => {
    if (!a.due_from) return 1;
    if (!b.due_from) return -1;
    return new Date(a.due_from).getTime() - new Date(b.due_from).getTime();
  });
}

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [editingHabit, setEditingHabit] = useState<Habit | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Habit | null>(null);
  const [checkInTarget, setCheckInTarget] = useState<Habit | null>(null);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["habits"],
    queryFn: () => habitsApi.getAll().then((r) => r.data),
  });

  const checkInMutation = useMutation({
    mutationFn: (id: string) => habitsApi.checkIn(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["habits"] });
      setCheckInTarget(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => habitsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["habits"] });
      setDeleteTarget(null);
    },
  });

  const openCreate = () => {
    setEditingHabit(null);
    setModalOpen(true);
  };
  const openEdit = (habit: Habit) => {
    setEditingHabit(habit);
    setModalOpen(true);
  };

  const sorted = data ? sortHabitsByDue(data.results) : [];

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      {/* Page header */}
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" color="text.primary">
            My Habits
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={0.5}>
            Track your progress and build streaks
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={openCreate}
          sx={{
            background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
            px: 3,
            py: 1.2,
            display: { xs: "none", sm: "flex" },
          }}
        >
          New Habit
        </Button>
      </Box>

      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}>
          <CircularProgress size={48} />
        </Box>
      )}
      {isError && <Alert severity="error">Failed to load habits.</Alert>}

      {data && data.count === 0 && (
        <Box
          sx={{
            textAlign: "center",
            py: 10,
            color: "text.secondary",
          }}
        >
          <Typography variant="h5" fontWeight="medium" mb={1}>
            No habits yet
          </Typography>
          <Typography variant="body2" mb={3}>
            Start building better routines by adding your first habit.
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>
            Add your first habit
          </Button>
        </Box>
      )}

      {/* Habit grid */}
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: "repeat(2, 1fr)",
            lg: "repeat(3, 1fr)",
          },
          gap: 2.5,
        }}
      >
        {sorted.map((habit) => {
          const status = getStatusInfo(habit);
          return (
            <HabitCard
              key={habit.id}
              habit={habit}
              status={status}
              checked={habit.is_checked}
              onCheckIn={() => setCheckInTarget(habit)}
              onEdit={() => openEdit(habit)}
              onDelete={() => setDeleteTarget(habit)}
              checkInLoading={checkInMutation.isPending && checkInMutation.variables === habit.id}
            />
          );
        })}
      </Box>

      {/* Mobile FAB */}
      <Zoom in>
        <Fab
          color="primary"
          aria-label="add habit"
          onClick={openCreate}
          sx={{
            position: "fixed",
            bottom: 24,
            right: 24,
            display: { sm: "none" },
            background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
          }}
        >
          <AddIcon />
        </Fab>
      </Zoom>

      <HabitModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        habit={editingHabit}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete habit?"
        message={`"${deleteTarget?.title}" will be permanently removed.`}
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
        onClose={() => setDeleteTarget(null)}
        loading={deleteMutation.isPending}
      />

      <CheckInModal
        open={!!checkInTarget}
        habit={checkInTarget}
        onConfirm={() => checkInTarget && checkInMutation.mutate(checkInTarget.id)}
        onClose={() => { setCheckInTarget(null); checkInMutation.reset(); }}
        loading={checkInMutation.isPending}
        error={extractCheckInError(checkInMutation.error)}
      />
    </Box>
  );
}

// ─── HabitCard sub-component ────────────────────────────────────────────────

interface HabitCardProps {
  habit: Habit;
  status: { label: string; color: "success" | "warning" | "error" | "default" };
  checked: boolean;
  onCheckIn: () => void;
  onEdit: () => void;
  onDelete: () => void;
  checkInLoading: boolean;
}

function HabitCard({
  habit,
  status,
  checked,
  onCheckIn,
  onEdit,
  onDelete,
  checkInLoading,
}: HabitCardProps) {
  const [hovered, setHovered] = useState(false);

  return (
    <Card
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      elevation={hovered ? 6 : 1}
      sx={{
        position: "relative",
        transition: "all 0.2s ease",
        transform: hovered ? "translateY(-2px)" : "none",
        border: checked ? "2px solid #10b981" : "2px solid transparent",
        backgroundColor: checked ? "#f0fdf4" : "white",
        cursor: "default",
        overflow: "visible",
      }}
    >
      {/* Hover action buttons (top-right overlay) */}
      <Box
        sx={{
          position: "absolute",
          top: -12,
          right: 8,
          display: "flex",
          gap: 0.5,
          opacity: hovered ? 1 : 0,
          transform: hovered ? "translateY(0)" : "translateY(4px)",
          transition: "all 0.2s ease",
          zIndex: 1,
        }}
      >
        <Tooltip title="Edit" arrow>
          <IconButton
            size="small"
            onClick={onEdit}
            sx={{
              backgroundColor: "white",
              boxShadow: 2,
              "&:hover": { backgroundColor: "#f1f5f9" },
            }}
          >
            <EditIcon fontSize="small" sx={{ color: "#4f46e5" }} />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete" arrow>
          <IconButton
            size="small"
            onClick={onDelete}
            sx={{
              backgroundColor: "white",
              boxShadow: 2,
              "&:hover": { backgroundColor: "#fef2f2" },
            }}
          >
            <DeleteIcon fontSize="small" sx={{ color: "#ef4444" }} />
          </IconButton>
        </Tooltip>
      </Box>

      <CardContent sx={{ pb: "16px !important" }}>
        {/* Title row */}
        <Box sx={{ display: "flex", alignItems: "flex-start", gap: 1, mb: 1.5 }}>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant="subtitle1"
              fontWeight={600}
              sx={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                textDecoration: checked ? "line-through" : "none",
                color: checked ? "text.secondary" : "text.primary",
              }}
            >
              {habit.title}
            </Typography>
          </Box>
        </Box>

        {/* Tags */}
        <Box sx={{ display: "flex", gap: 0.75, flexWrap: "wrap", mb: 2 }}>
          <Chip
            label={habit.periodicity.replace(/_/g, " ")}
            size="small"
            color={PERIODICITY_COLORS[habit.periodicity] ?? "default"}
            variant="outlined"
            sx={{ fontSize: "0.7rem" }}
          />
          {habit.list_title && (
            <Chip
              label={habit.list_title}
              size="small"
              variant="outlined"
              sx={{ fontSize: "0.7rem" }}
            />
          )}
          <Chip
            label={status.label}
            size="small"
            color={status.color}
            variant={status.color === "default" ? "outlined" : "filled"}
            sx={{ fontSize: "0.7rem" }}
          />
        </Box>

        {/* Streak + check-in */}
        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <LocalFireDepartmentIcon sx={{ fontSize: 16, color: "#f59e0b" }} />
            <Typography variant="body2" fontWeight={600} color="#92400e">
              {habit.streak_count} streak
            </Typography>
          </Box>

          <Tooltip title={checked ? "Already checked in" : "Check in"} arrow>
            <span>
              <IconButton
                size="small"
                onClick={onCheckIn}
                disabled={checked || checkInLoading}
                sx={{
                  color: checked ? "#10b981" : "#4f46e5",
                  transition: "transform 0.15s",
                  "&:active": { transform: "scale(0.9)" },
                }}
              >
                {checked ? (
                  <CheckCircleIcon />
                ) : (
                  <CheckCircleOutlineIcon />
                )}
              </IconButton>
            </span>
          </Tooltip>
        </Box>

        {/* Due date */}
        {habit.due_to && (
          <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 1 }}>
            Due {new Date(habit.due_to).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
