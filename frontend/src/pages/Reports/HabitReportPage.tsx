import React from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import LocalFireDepartmentIcon from "@mui/icons-material/LocalFireDepartment";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/api/endpoints/reports";

export default function HabitReportPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["report-habit", id],
    queryFn: () => reportsApi.habit(id!).then((r) => r.data),
    enabled: !!id,
  });

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate("/reports")}
        sx={{ mb: 3, color: "text.secondary" }}
      >
        Back to Reports
      </Button>

      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}>
          <CircularProgress size={48} />
        </Box>
      )}
      {isError && <Alert severity="error">Failed to load habit report.</Alert>}

      {data && (
        <>
          <Typography variant="h4" fontWeight="bold" mb={1}>
            {data.title}
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={4}>
            Habit performance overview
          </Typography>

          {/* Stat cards */}
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr 1fr", md: "repeat(3, 1fr)" },
              gap: 2,
              mb: 4,
            }}
          >
            <Card elevation={1}>
              <CardContent>
                <Box sx={{ width: 40, height: 40, borderRadius: 2, backgroundColor: "#fef3c7", display: "flex", alignItems: "center", justifyContent: "center", mb: 1.5 }}>
                  <LocalFireDepartmentIcon sx={{ color: "#f59e0b" }} />
                </Box>
                <Typography variant="h5" fontWeight={700}>{data.streak_count} 🔥</Typography>
                <Typography variant="body2" color="text.secondary">Current Streak</Typography>
              </CardContent>
            </Card>

            <Card elevation={1}>
              <CardContent>
                <Box sx={{ width: 40, height: 40, borderRadius: 2, backgroundColor: "#ede9fe", display: "flex", alignItems: "center", justifyContent: "center", mb: 1.5 }}>
                  <LocalFireDepartmentIcon sx={{ color: "#7c3aed" }} />
                </Box>
                <Typography variant="h5" fontWeight={700}>{data.longest_streak} 🔥</Typography>
                <Typography variant="body2" color="text.secondary">Longest Streak</Typography>
              </CardContent>
            </Card>

            <Card elevation={1}>
              <CardContent>
                <Box sx={{ width: 40, height: 40, borderRadius: 2, backgroundColor: "#d1fae5", display: "flex", alignItems: "center", justifyContent: "center", mb: 1.5 }}>
                  <CheckCircleIcon sx={{ color: "#10b981" }} />
                </Box>
                <Typography variant="h5" fontWeight={700}>{data.log_history.length}</Typography>
                <Typography variant="body2" color="text.secondary">Total Check-ins</Typography>
              </CardContent>
            </Card>
          </Box>

          <Divider sx={{ mb: 3 }} />

          <Typography variant="h5" fontWeight={600} mb={2}>
            Check-in History
          </Typography>

          {data.log_history.length === 0 ? (
            <Alert severity="info">No check-ins recorded yet.</Alert>
          ) : (
            <Paper elevation={1} sx={{ borderRadius: 3, overflow: "hidden" }}>
              <List dense disablePadding>
                {data.log_history.map((log, idx) => (
                  <ListItem
                    key={log.id}
                    divider={idx < data.log_history.length - 1}
                    sx={{ py: 1.5 }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <CheckCircleIcon sx={{ color: "#10b981", fontSize: 18 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={new Date(log.checked_at).toLocaleString(undefined, {
                        weekday: "long",
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                      primaryTypographyProps={{ variant: "body2", fontWeight: 500 }}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}
        </>
      )}
    </Box>
  );
}
