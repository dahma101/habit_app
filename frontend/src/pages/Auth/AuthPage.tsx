import React, { useState } from "react";
import {
  Alert,
  Avatar,
  Box,
  Button,
  Container,
  Paper,
  Tab,
  Tabs,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import {
  loginSchema,
  registerSchema,
  type LoginFormData,
  type RegisterFormData,
} from "@/schemas/auth";
import { authApi } from "@/api/endpoints/auth";
import { useAuthStore } from "@/store/authStore";
import { avatarList } from "@/assets/avatars";

function extractApiError(err: unknown): string {
  if (err && typeof err === "object" && "response" in err) {
    const data = (err as { response?: { data?: unknown } }).response?.data;
    if (data && typeof data === "object") {
      const d = data as Record<string, unknown>;
      if (typeof d.detail === "string") return d.detail;
      const messages: string[] = [];
      for (const [key, val] of Object.entries(d)) {
        const prefix = key === "non_field_errors" ? "" : `${key}: `;
        if (Array.isArray(val)) messages.push(prefix + val.join(", "));
        else if (typeof val === "string") messages.push(prefix + val);
      }
      if (messages.length) return messages.join(" | ");
    }
  }
  return "An unexpected error occurred. Please try again.";
}

export default function AuthPage() {
  const [tab, setTab] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { setTokens } = useAuthStore();

  const loginForm = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });
  const registerForm = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: { avatar: "avatar1" },
  });

  const handleLogin = async (data: LoginFormData) => {
    setError(null);
    try {
      const res = await authApi.login(data);
      setTokens(res.data.access, res.data.refresh, res.data.user);
      navigate("/dashboard");
    } catch (err) {
      setError(extractApiError(err));
    }
  };

  const handleRegister = async (data: RegisterFormData) => {
    setError(null);
    try {
      const res = await authApi.register(data);
      setTokens(res.data.access, res.data.refresh, res.data.user);
      navigate("/dashboard");
    } catch (err) {
      setError(extractApiError(err));
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #1e1b4b 0%, #4f46e5 50%, #7c3aed 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        p: 2,
      }}
    >
      <Container maxWidth="sm">
        {/* Hero text */}
        <Box sx={{ textAlign: "center", mb: 4 }}>
          <Typography variant="h3" fontWeight="bold" sx={{ color: "white", mb: 1 }}>
            IU Habit App
          </Typography>
          <Typography variant="body1" sx={{ color: "rgba(255,255,255,0.75)" }}>
            Build consistency, one habit at a time
          </Typography>
        </Box>

        <Paper
          elevation={24}
          sx={{
            borderRadius: 3,
            overflow: "hidden",
            backdropFilter: "blur(20px)",
          }}
        >
          <Tabs
            value={tab}
            onChange={(_, v: number) => {
              setTab(v);
              setError(null);
            }}
            variant="fullWidth"
            sx={{
              backgroundColor: "#f1f5f9",
              "& .MuiTab-root": { py: 2, fontWeight: 600 },
              "& .MuiTabs-indicator": { height: 3 },
            }}
          >
            <Tab label="Sign In" />
            <Tab label="Create Account" />
          </Tabs>

          <Box sx={{ p: 4 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {/* Login Tab */}
            {tab === 0 && (
              <Box
                component="form"
                sx={{ display: "flex", flexDirection: "column", gap: 2.5 }}
              >
                <TextField
                  label="Email address"
                  type="email"
                  fullWidth
                  {...loginForm.register("email")}
                  error={!!loginForm.formState.errors.email}
                  helperText={loginForm.formState.errors.email?.message}
                />
                <TextField
                  label="Password"
                  type="password"
                  fullWidth
                  {...loginForm.register("password")}
                  error={!!loginForm.formState.errors.password}
                  helperText={loginForm.formState.errors.password?.message}
                />
                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  onClick={loginForm.handleSubmit(handleLogin)}
                  disabled={loginForm.formState.isSubmitting}
                  sx={{
                    py: 1.5,
                    background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                    "&:hover": {
                      background: "linear-gradient(135deg, #4338ca 0%, #6d28d9 100%)",
                    },
                  }}
                >
                  {loginForm.formState.isSubmitting ? "Signing in…" : "Sign In"}
                </Button>
              </Box>
            )}

            {/* Register Tab */}
            {tab === 1 && (
              <Box
                component="form"
                sx={{ display: "flex", flexDirection: "column", gap: 2.5 }}
              >
                <TextField
                  label="Full name"
                  fullWidth
                  {...registerForm.register("full_name")}
                  error={!!registerForm.formState.errors.full_name}
                  helperText={registerForm.formState.errors.full_name?.message}
                />
                <TextField
                  label="Email address"
                  type="email"
                  fullWidth
                  {...registerForm.register("email")}
                  error={!!registerForm.formState.errors.email}
                  helperText={registerForm.formState.errors.email?.message}
                />
                <TextField
                  label="Password (min 8 characters)"
                  type="password"
                  fullWidth
                  {...registerForm.register("password")}
                  error={!!registerForm.formState.errors.password}
                  helperText={registerForm.formState.errors.password?.message}
                />

                {/* Avatar picker */}
                <Box>
                  <Typography variant="body2" fontWeight={600} mb={1.5} color="text.secondary">
                    Choose your avatar
                  </Typography>
                  <Controller
                    name="avatar"
                    control={registerForm.control}
                    render={({ field }) => (
                      <Box sx={{ display: "flex", gap: 1.5, flexWrap: "wrap" }}>
                        {avatarList.map((av) => (
                          <Tooltip key={av.key} title={av.label} arrow>
                            <Box
                              onClick={() => field.onChange(av.key)}
                              sx={{
                                cursor: "pointer",
                                borderRadius: "50%",
                                border: field.value === av.key
                                  ? "3px solid #4f46e5"
                                  : "3px solid transparent",
                                transition: "all 0.2s",
                                transform: field.value === av.key ? "scale(1.1)" : "scale(1)",
                                "&:hover": { transform: "scale(1.08)" },
                              }}
                            >
                              <Avatar
                                src={av.src}
                                sx={{ width: 56, height: 56 }}
                              />
                            </Box>
                          </Tooltip>
                        ))}
                      </Box>
                    )}
                  />
                  {registerForm.formState.errors.avatar && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                      {registerForm.formState.errors.avatar.message}
                    </Typography>
                  )}
                </Box>

                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  onClick={registerForm.handleSubmit(handleRegister)}
                  disabled={registerForm.formState.isSubmitting}
                  sx={{
                    py: 1.5,
                    background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                    "&:hover": {
                      background: "linear-gradient(135deg, #4338ca 0%, #6d28d9 100%)",
                    },
                  }}
                >
                  {registerForm.formState.isSubmitting ? "Creating account…" : "Create Account"}
                </Button>
              </Box>
            )}
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}
