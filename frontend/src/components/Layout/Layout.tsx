import React, { useState } from "react";
import {
  AppBar,
  Avatar,
  Box,
  Button,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ListAltIcon from "@mui/icons-material/ListAlt";
import BarChartIcon from "@mui/icons-material/BarChart";
import LogoutIcon from "@mui/icons-material/Logout";
import LoginIcon from "@mui/icons-material/Login";

import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { avatarMap } from "@/assets/avatars";

const DRAWER_WIDTH = 240;

const navItems = [
  { label: "Dashboard", icon: <DashboardIcon />, path: "/dashboard" },
  { label: "Lists", icon: <ListAltIcon />, path: "/lists" },
  { label: "Analytics (Progress)", icon: <BarChartIcon />, path: "/reports" },
];

interface Props {
  children: React.ReactNode;
}

export default function Layout({ children }: Props) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const [drawerOpen, setDrawerOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  const handleNav = (path: string) => {
    navigate(path);
    if (isMobile) setDrawerOpen(false);
  };

  const drawerContent = (
    <Box
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        background: "linear-gradient(180deg, #1e1b4b 0%, #312e81 100%)",
        color: "white",
      }}
    >
      {/* Logo */}
      <Box sx={{ p: 3, pb: 2 }}>
        <Typography
          variant="h6"
          fontWeight="bold"
          sx={{ color: "white", letterSpacing: 0.5 }}
        >
          MeinHabit
        </Typography>
        <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
          Build better habits
        </Typography>
      </Box>

      <Divider sx={{ borderColor: "rgba(255,255,255,0.15)" }} />

      {/* User info */}
      {user && (
        <Box sx={{ px: 2, py: 2, display: "flex", alignItems: "center", gap: 1.5 }}>
          <Avatar
            src={avatarMap[user.avatar]}
            sx={{ width: 40, height: 40, border: "2px solid rgba(255,255,255,0.3)" }}
          />
          <Box sx={{ minWidth: 0 }}>
            <Typography
              variant="body2"
              fontWeight="medium"
              sx={{ color: "white", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
            >
              {user.full_name}
            </Typography>
            <Typography
              variant="caption"
              sx={{ color: "rgba(255,255,255,0.5)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", display: "block" }}
            >
              {user.email}
            </Typography>
          </Box>
        </Box>
      )}

      <Divider sx={{ borderColor: "rgba(255,255,255,0.15)" }} />

      {/* Navigation */}
      <List sx={{ flex: 1, pt: 1 }}>
        {navItems.map((item) => {
          const active = location.pathname.startsWith(item.path);
          return (
            <ListItem key={item.path} disablePadding sx={{ px: 1, mb: 0.5 }}>
              <ListItemButton
                onClick={() => handleNav(item.path)}
                sx={{
                  borderRadius: 2,
                  backgroundColor: active
                    ? "rgba(255,255,255,0.15)"
                    : "transparent",
                  "&:hover": { backgroundColor: "rgba(255,255,255,0.1)" },
                  transition: "background-color 0.2s",
                }}
              >
                <ListItemIcon
                  sx={{ color: active ? "white" : "rgba(255,255,255,0.6)", minWidth: 40 }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    fontWeight: active ? 600 : 400,
                    color: active ? "white" : "rgba(255,255,255,0.7)",
                    fontSize: "0.875rem",
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      {/* Desktop permanent drawer */}
      {!isMobile && (
        <Drawer
          variant="permanent"
          sx={{
            width: DRAWER_WIDTH,
            flexShrink: 0,
            "& .MuiDrawer-paper": {
              width: DRAWER_WIDTH,
              boxSizing: "border-box",
              border: "none",
            },
          }}
        >
          {drawerContent}
        </Drawer>
      )}

      {/* Mobile temporary drawer */}
      {isMobile && (
        <Drawer
          variant="temporary"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          sx={{
            "& .MuiDrawer-paper": {
              width: DRAWER_WIDTH,
              boxSizing: "border-box",
              border: "none",
            },
          }}
        >
          {drawerContent}
        </Drawer>
      )}

      {/* Main content area */}
      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          minWidth: 0,
          backgroundColor: "#f8fafc",
        }}
      >
        {/* Top AppBar */}
        <AppBar
          position="sticky"
          elevation={0}
          sx={{
            backgroundColor: "white",
            borderBottom: "1px solid #e2e8f0",
            color: "text.primary",
          }}
        >
          <Toolbar>
            {isMobile && (
              <IconButton
                edge="start"
                onClick={() => setDrawerOpen(true)}
                sx={{ mr: 1 }}
              >
                <MenuIcon />
              </IconButton>
            )}

            {isMobile && (
              <Typography variant="h6" fontWeight="bold" sx={{ flexGrow: 1, color: "#1e1b4b" }}>
                MeinHabit
              </Typography>
            )}

            {!isMobile && <Box sx={{ flexGrow: 1 }} />}

            {/* Header right: login/logout */}
            {isAuthenticated ? (
              <Button
                onClick={logout}
                startIcon={<LogoutIcon />}
                color="inherit"
                sx={{ color: "text.secondary", fontWeight: 500 }}
              >
                Logout
              </Button>
            ) : (
              <Button
                onClick={() => navigate("/auth")}
                startIcon={<LoginIcon />}
                color="inherit"
                sx={{ color: "text.secondary", fontWeight: 500 }}
              >
                Login
              </Button>
            )}
          </Toolbar>
        </AppBar>

        {/* Page content */}
        <Box sx={{ flex: 1, overflow: "auto" }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}
