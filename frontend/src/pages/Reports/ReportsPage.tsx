import React from "react";
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import LocalFireDepartmentIcon from "@mui/icons-material/LocalFireDepartment";
import TrackChangesIcon from "@mui/icons-material/TrackChanges";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { reportsApi } from "@/api/endpoints/reports";

const PERIODICITY_COLORS: Record<string, "primary" | "secondary" | "success" | "warning" | "info"> = {
  as_many_as_possible: "info",
  daily: "primary",
  twice_weekly: "secondary",
  weekly: "success",
  twice_monthly: "warning",
  monthly: "info",
};

export default function ReportsPage() {
  const navigate = useNavigate();

  const { data: general, isLoading: loadingGeneral, isError: errorGeneral } = useQuery({
    queryKey: ["report-general"],
    queryFn: () => reportsApi.general().then((r) => r.data),
  });

  const { data: allHabits, isLoading: loadingAll, isError: errorAll } = useQuery({
    queryKey: ["report-all"],
    queryFn: () => reportsApi.all().then((r) => r.data),
  });

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold">
          Overall Progress
        </Typography>
        <Typography variant="body2" color="text.secondary" mt={0.5}>
          Insights and analytics for all your habits
        </Typography>
      </Box>

      <Typography variant="h5" fontWeight={600} mb={2}>
        Summary
      </Typography>

      {loadingGeneral && <CircularProgress />}
      {errorGeneral && <Alert severity="error" sx={{ mb: 3 }}>Failed to load summary.</Alert>}

      {general && (
        <>
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr 1fr", md: "repeat(4, 1fr)" },
              gap: 2,
              mb: 4,
            }}
          >
            <StatCard
              label="Total Habits"
              value={general.tracked_habits.length}
              icon={<TrackChangesIcon sx={{ color: "#4f46e5" }} />}
              bg="#ede9fe"
            />
            <StatCard
              label="Longest Streak"
              value={`${general.longest_streak} 🔥`}
              icon={<LocalFireDepartmentIcon sx={{ color: "#f59e0b" }} />}
              bg="#fef3c7"
            />
            <StatCard
              label="Periodicities"
              value={Object.keys(general.habits_by_periodicity).length}
              icon={<TrackChangesIcon sx={{ color: "#10b981" }} />}
              bg="#d1fae5"
            />
            <StatCard
              label="Least Tracked"
              value={general.least_tracked_habit?.title ?? "—"}
              icon={<TrendingDownIcon sx={{ color: "#ef4444" }} />}
              bg="#fee2e2"
            />
          </Box>

          <Paper sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" fontWeight={600} mb={2}>
              Habits by Frequency
            </Typography>
            <Box sx={{ display: "flex", gap: 1.5, flexWrap: "wrap" }}>
              {Object.entries(general.habits_by_periodicity).map(([period, habits]) => (
                <Chip
                  key={period}
                  label={`${period.replace(/_/g, " ")} · ${habits.length}`}
                  color={PERIODICITY_COLORS[period] ?? "default"}
                  variant="outlined"
                  sx={{ fontWeight: 600 }}
                />
              ))}
            </Box>
          </Paper>
        </>
      )}

      <Divider sx={{ mb: 4 }} />

      <Typography variant="h5" fontWeight={600} mb={2}>
        All Habits
        <Typography component="span" variant="body2" color="text.secondary" ml={1}>
          — click a name to view its report
        </Typography>
      </Typography>

      {loadingAll && <CircularProgress />}
      {errorAll && <Alert severity="error">Failed to load habits.</Alert>}

      {allHabits && (
        <TableContainer component={Paper} elevation={1} sx={{ borderRadius: 3, overflow: "hidden" }}>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: "#f8fafc" }}>
                <TableCell sx={{ fontWeight: 700 }}>Habit</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Frequency</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Streak</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>List</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {allHabits.results.map((habit) => (
                <TableRow
                  key={habit.id}
                  hover
                  sx={{ cursor: "pointer" }}
                  onClick={() => navigate(`/reports/habit/${habit.id}`)}
                >
                  <TableCell>
                    <Typography variant="body2" fontWeight={600} sx={{ color: "#4f46e5" }}>
                      {habit.title}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={habit.periodicity.replace(/_/g, " ")}
                      size="small"
                      color={PERIODICITY_COLORS[habit.periodicity] ?? "default"}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                      <LocalFireDepartmentIcon sx={{ fontSize: 14, color: "#f59e0b" }} />
                      <Typography variant="body2" fontWeight={600}>{habit.streak_count}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">{habit.list_title ?? "—"}</Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}

function StatCard({
  label,
  value,
  icon,
  bg,
}: {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  bg: string;
}) {
  return (
    <Card elevation={1}>
      <CardContent>
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: 2,
            backgroundColor: bg,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            mb: 1.5,
          }}
        >
          {icon}
        </Box>
        <Typography variant="h5" fontWeight={700}>{value}</Typography>
        <Typography variant="body2" color="text.secondary">{label}</Typography>
      </CardContent>
    </Card>
  );
}
