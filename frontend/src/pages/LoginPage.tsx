import { useState } from "react";
import { Link, useNavigate } from "react-router";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import React from "react";
import { motion } from "framer-motion";
import Lottie from "lottie-react";
import { Eye, EyeOff } from "lucide-react";
import loginAnimation from "@/imports/Login.json";
import { VisualBackground } from "@/components/VisualBackground";

export default function LoginPage() {
  const navigate = useNavigate();
  const [role, setRole] = React.useState("applicant");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/auth/login", {
        email,
        password
      });
      
      const userRole = response.data.role || role;
      const userId = response.data.user_id;
      
      if (userId) {
        localStorage.setItem("user_id", userId);
        localStorage.setItem("user_role", userRole);
        localStorage.setItem("access_token", response.data.access_token);

        // Fetch the full profile right away so name/avatar appear immediately
        // without needing to hit "Save Changes" on the profile page.
        try {
          const profileRes = await axios.get(`http://127.0.0.1:5000/api/profile/${userId}`);
          const p = profileRes.data;
          if (p.name) {
            localStorage.setItem("user_name", p.name);
          } else {
            localStorage.removeItem("user_name");
          }
          if (p.avatar_url) {
            localStorage.setItem("avatar_url", p.avatar_url);
          } else {
            localStorage.removeItem("avatar_url");
          }
          if (p.job_title) {
            localStorage.setItem("user_job_title", p.job_title);
          } else {
            localStorage.removeItem("user_job_title");
          }
          if (p.company) {
            localStorage.setItem("company", p.company);
          } else {
            localStorage.removeItem("company");
          }
        } catch {
          // Profile fetch failed — not critical, user can still log in
        }
      }
      
      if (userRole === "applicant") {
        navigate("/applicant/dashboard");
      } else {
        navigate("/recruiter/dashboard");
      }
    } catch (err: any) {
      console.error("Login error:", err);
      const message = err.response?.data?.error || err.message || "Login failed. Please check if the backend is running.";
      setError(message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden selection:bg-[#F97316] selection:text-white">
      <VisualBackground />
      
      <div className="w-full max-w-5xl flex items-center justify-between gap-12 relative z-10">
        {/* Animation Side */}
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="flex-1 hidden md:flex items-center justify-center"
        >
          <div className="w-full max-w-lg drop-shadow-2xl">
            <Lottie
              animationData={loginAnimation}
              loop={true}
              autoplay={true}
              style={{ width: '100%', height: 'auto' }}
            />
          </div>
        </motion.div>

        {/* Card Side */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="w-full max-w-md"
        >
          <Card className="shadow-2xl border-none bg-white/95 backdrop-blur-sm">
            <CardHeader className="space-y-3 text-center pb-6">
              <div className="flex justify-center mb-2">
                <Link to="/" className="text-4xl font-black tracking-tighter text-[#1E3A5F]">SipSetu</Link>
              </div>
              <CardTitle className="text-2xl font-bold">Welcome back</CardTitle>
              <CardDescription>Enter your details to sign in to your account</CardDescription>
            </CardHeader>
            <CardContent>
          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-2">
              <Label className="text-slate-600 text-xs uppercase tracking-wider font-semibold">I am a</Label>
              <ToggleGroup 
                type="single" 
                value={role} 
                onValueChange={(v) => v && setRole(v)}
                className="justify-start w-full bg-slate-100 p-1 rounded-xl"
              >
                <ToggleGroupItem 
                  value="applicant" 
                  className={`flex-1 rounded-lg data-[state=on]:bg-[#1E3A5F] data-[state=on]:text-black ${role !== 'applicant' && 'hover:bg-slate-200 text-slate-600'}`}
                >
                  Job Seeker
                </ToggleGroupItem>
                <ToggleGroupItem 
                  value="recruiter" 
                  className={`flex-1 rounded-lg data-[state=on]:bg-[#1E3A5F] data-[state=on]:text-black ${role !== 'recruiter' && 'hover:bg-slate-200 text-slate-600'}`}
                >
                  Recruiter
                </ToggleGroupItem>
              </ToggleGroup>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" placeholder="name@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required className="h-11" />
              </div>
                <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Password</Label>
                </div>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="h-11 pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="absolute inset-y-0 right-3 flex items-center text-slate-500"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>
            </div>
            
            {error && <p className="text-red-500 text-sm">{error}</p>}

            <Button type="submit" className="w-full h-11 text-base bg-[#1E3A5F] hover:bg-[#1E3A5F]/90">
              Sign In
            </Button>

            <div className="text-center text-sm text-slate-600">
              Don't have an account?{" "}
              <Link to={`/register?role=${role}`} className="font-medium text-[#1E3A5F] hover:underline">
                Register
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  </div>
</div>
  );
}
