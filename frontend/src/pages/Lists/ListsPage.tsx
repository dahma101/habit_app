import React, { useState } from "react";
import {
  Alert,
  Box,
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
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import ListAltIcon from "@mui/icons-material/ListAlt";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listsApi } from "@/api/endpoints/lists";
import ListModal from "@/components/modals/ListModal";
import ConfirmDialog from "@/components/modals/ConfirmDialog";
import type { HabitList } from "@/types";

export default function ListsPage() {
  const queryClient = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [editingList, setEditingList] = useState<HabitList | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<HabitList | null>(null);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["lists"],
    queryFn: () => listsApi.getAll().then((r) => r.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => listsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lists"] });
      setDeleteTarget(null);
    },
    onError: () => alert("Could not delete list."),
  });

  const openCreate = () => {
    setEditingList(null);
    setModalOpen(true);
  };
  const openEdit = (list: HabitList) => {
    setEditingList(list);
    setModalOpen(true);
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" color="text.primary">
          My Lists
        </Typography>
        <Typography variant="body2" color="text.secondary" mt={0.5}>
          Organise your habits into categories
        </Typography>
      </Box>

      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}>
          <CircularProgress size={48} />
        </Box>
      )}
      {isError && <Alert severity="error">Failed to load lists.</Alert>}

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: "repeat(2, 1fr)",
            md: "repeat(3, 1fr)",
          },
          gap: 2.5,
        }}
      >
        {data?.results.map((list) => (
          <ListCard
            key={list.id}
            list={list}
            onEdit={() => openEdit(list)}
            onDelete={() => setDeleteTarget(list)}
          />
        ))}
      </Box>

      <Zoom in>
        <Fab
          color="primary"
          aria-label="add list"
          onClick={openCreate}
          sx={{
            position: "fixed",
            bottom: 24,
            right: 24,
            background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
          }}
        >
          <AddIcon />
        </Fab>
      </Zoom>

      <ListModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        list={editingList}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete list?"
        message={`"${deleteTarget?.title}" will be deleted and its habits moved to Default.`}
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
        onClose={() => setDeleteTarget(null)}
        loading={deleteMutation.isPending}
      />
    </Box>
  );
}

// ─── ListCard sub-component ────────────────────────────────────────────────

interface ListCardProps {
  list: HabitList;
  onEdit: () => void;
  onDelete: () => void;
}

function ListCard({ list, onEdit, onDelete }: ListCardProps) {
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
        border: list.is_default ? "2px solid #4f46e5" : "2px solid transparent",
        overflow: "visible",
      }}
    >
      {/* Hover actions */}
      {!list.is_default && (
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
              sx={{ backgroundColor: "white", boxShadow: 2 }}
            >
              <EditIcon fontSize="small" sx={{ color: "#4f46e5" }} />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete" arrow>
            <IconButton
              size="small"
              onClick={onDelete}
              sx={{ backgroundColor: "white", boxShadow: 2 }}
            >
              <DeleteIcon fontSize="small" sx={{ color: "#ef4444" }} />
            </IconButton>
          </Tooltip>
        </Box>
      )}

      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 1.5 }}>
          <Box
            sx={{
              p: 1,
              borderRadius: 2,
              backgroundColor: list.is_default ? "#ede9fe" : "#f1f5f9",
              display: "flex",
            }}
          >
            <ListAltIcon sx={{ color: list.is_default ? "#7c3aed" : "#64748b", fontSize: 20 }} />
          </Box>
          <Typography variant="subtitle1" fontWeight={600} sx={{ flex: 1 }}>
            {list.title}
          </Typography>
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          {list.is_default && (
            <Chip label="Default" size="small" color="secondary" variant="outlined" />
          )}
          <Typography variant="caption" color="text.secondary" sx={{ ml: "auto" }}>
            {new Date(list.created_at).toLocaleDateString()}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
