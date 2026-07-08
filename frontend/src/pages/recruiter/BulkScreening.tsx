import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Briefcase,
  Users,
  ChevronRight,
  CheckCircle2,
  XCircle,
  Eye,
  Loader2,
  Star,
  AlertCircle,
  Search,
  UserCheck,
  TrendingUp,
  Clock,
} from "lucide-react";
import axios from "axios";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

const API = "http://localhost:5000/api";

interface Job {
  job_id: string;
  title: string;
  skills: string[];
  experience_level?: string;
  location?: string;
  created_at?: string;
}

interface Candidate {
  application_id: string;
  applicant_id: string;
  name: string;
  email: string;
  phone: string;
  skills: string[];
  matched_skills: string[];
  missing_skills: string[];
  match_score: number;
  experience_years: number;
  experience_score: number;
  composite_score: number;
  status: "applied" | "reviewed" | "shortlisted" | "rejected";
  applied_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  applied: "bg-blue-100 text-blue-700",
  reviewed: "bg-amber-100 text-amber-700",
  shortlisted: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
};

const STATUS_LABELS: Record<string, string> = {
  applied: "Applied",
  reviewed: "Reviewed",
  shortlisted: "Shortlisted",
  rejected: "Rejected",
};

export default function RecruiterBulkScreening() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [candidatesLoading, setCandidatesLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState<string | null>(null);

  const token = localStorage.getItem("access_token");
  const recruiterId = localStorage.getItem("user_id");

  // Fetch recruiter's posted jobs
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await axios.get(`${API}/jobs`, {
          params: { recruiter_id: recruiterId },
        });
        const myJobs: Job[] = res.data.jobs || [];
        setJobs(myJobs);
        if (myJobs.length > 0) {
          setSelectedJob(myJobs[0]);
        }
      } catch (err) {
        console.error("Failed to load jobs", err);
      } finally {
        setJobsLoading(false);
      }
    };
    if (recruiterId) fetchJobs();
  }, [recruiterId]);

  // Fetch candidates for selected job
  useEffect(() => {
    if (!selectedJob) return;
    const fetchCandidates = async () => {
      setCandidatesLoading(true);
      try {
        const res = await axios.get(`${API}/jobs/${selectedJob.job_id}/applications`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setCandidates(res.data.applications || []);
      } catch (err) {
        console.error("Failed to load candidates", err);
        setCandidates([]);
      } finally {
        setCandidatesLoading(false);
      }
    };
    fetchCandidates();
  }, [selectedJob, token]);

  const handleStatusUpdate = async (candidate: Candidate, newStatus: string) => {
    if (!selectedJob) return;
    setUpdatingStatus(candidate.application_id);
    try {
      await axios.patch(
        `${API}/jobs/${selectedJob.job_id}/applications/${candidate.application_id}`,
        { status: newStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCandidates((prev) =>
        prev.map((c) =>
          c.application_id === candidate.application_id ? { ...c, status: newStatus as any } : c
        )
      );
      if (selectedCandidate?.application_id === candidate.application_id) {
        setSelectedCandidate((prev) => prev ? { ...prev, status: newStatus as any } : prev);
      }
    } catch (err) {
      console.error("Status update failed", err);
    } finally {
      setUpdatingStatus(null);
    }
  };

  const filteredCandidates = candidates.filter((c) =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const shortlisted = candidates.filter((c) => c.status === "shortlisted").length;
  const topScore = candidates.length > 0 ? candidates[0].match_score : 0;

  const getInitials = (name: string) =>
    name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2) || "??";

  const scoreColor = (score: number) =>
    score >= 75 ? "text-green-600" : score >= 50 ? "text-orange-500" : "text-slate-400";

  const scoreBg = (score: number) =>
    score >= 75 ? "bg-green-500" : score >= 50 ? "bg-orange-500" : "bg-slate-300";

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-16">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
          <Users className="h-7 w-7 text-[#1E3A5F]" /> Candidates
        </h1>
        <p className="text-slate-500 mt-1">
          View and manage applicants who applied to your job postings.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left: Job List */}
        <div className="lg:col-span-1 space-y-3">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 px-1">Your Jobs</h2>

          {jobsLoading ? (
            <div className="flex items-center justify-center py-10">
              <Loader2 className="h-6 w-6 animate-spin text-[#F97316]" />
            </div>
          ) : jobs.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
              <Briefcase className="h-8 w-8 mx-auto mb-2 text-slate-300" />
              No jobs posted yet.<br />
              <span className="text-[#F97316] font-semibold">Post a job</span> to start receiving candidates.
            </div>
          ) : (
            jobs.map((job) => {
              const isSelected = selectedJob?.job_id === job.job_id;
              return (
                <button
                  key={job.job_id}
                  onClick={() => { setSelectedJob(job); setSearchQuery(""); }}
                  className={`w-full text-left p-3 rounded-xl border transition-all duration-150 ${
                    isSelected
                      ? "bg-[#1E3A5F] text-white border-[#1E3A5F] shadow-md"
                      : "bg-white text-slate-800 border-slate-200 hover:border-[#1E3A5F]/40 hover:bg-slate-50"
                  }`}
                >
                  <p className={`font-semibold text-sm truncate ${isSelected ? "text-white" : "text-slate-900"}`}>
                    {job.title}
                  </p>
                  {job.location && (
                    <p className={`text-xs mt-0.5 truncate ${isSelected ? "text-white/70" : "text-slate-500"}`}>
                      {job.location}
                    </p>
                  )}
                  <div className="flex flex-wrap gap-1 mt-2">
                    {(job.skills || []).slice(0, 2).map((s) => (
                      <span
                        key={s}
                        className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                          isSelected ? "bg-white/20 text-white" : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Right: Candidates Panel */}
        <div className="lg:col-span-3 space-y-4">
          {!selectedJob ? (
            <div className="flex flex-col items-center justify-center h-64 rounded-2xl border border-dashed border-slate-200 bg-slate-50">
              <Users className="h-12 w-12 text-slate-300 mb-3" />
              <p className="text-slate-500 font-medium">Select a job to view candidates</p>
            </div>
          ) : (
            <>
              {/* Job Header + Stats */}
              <div className="bg-gradient-to-r from-[#1E3A5F] to-[#1E3A5F]/80 rounded-2xl p-5 text-white">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div>
                    <p className="text-white/60 text-xs font-semibold uppercase tracking-wider mb-1">Selected Job</p>
                    <h2 className="text-xl font-bold">{selectedJob.title}</h2>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {(selectedJob.skills || []).map((s) => (
                        <span key={s} className="text-[10px] bg-white/20 text-white px-2 py-0.5 rounded-full font-medium">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="text-center">
                      <p className="text-2xl font-black">{candidates.length}</p>
                      <p className="text-white/60 text-xs">Applicants</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-black">{shortlisted}</p>
                      <p className="text-white/60 text-xs">Shortlisted</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-black">{topScore}%</p>
                      <p className="text-white/60 text-xs">Top Match</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search candidates by name or email..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 bg-white border-slate-200"
                />
              </div>

              {/* Candidates List */}
              {candidatesLoading ? (
                <div className="flex items-center justify-center py-16">
                  <Loader2 className="h-8 w-8 animate-spin text-[#F97316]" />
                </div>
              ) : filteredCandidates.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-slate-200 bg-white p-12 text-center">
                  <div className="h-16 w-16 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-4">
                    <UserCheck className="h-8 w-8 text-slate-300" />
                  </div>
                  <h3 className="font-bold text-slate-800 text-lg mb-1">No candidates yet</h3>
                  <p className="text-slate-500 text-sm max-w-sm mx-auto">
                    {candidates.length === 0
                      ? "Candidates who apply to this job will appear here, ranked by how well their resume matches your requirements."
                      : "No candidates match your search."}
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredCandidates.map((candidate, index) => {
                    const isTop = index === 0 && candidate.match_score > 0;
                    const initials = getInitials(candidate.name);
                    const isUpdating = updatingStatus === candidate.application_id;

                    return (
                      <Card
                        key={candidate.application_id}
                        className={`border shadow-sm hover:shadow-md transition-all duration-200 ${
                          isTop ? "border-orange-200 bg-orange-50/20" : "border-slate-200 bg-white"
                        }`}
                      >
                        <CardContent className="p-4 md:p-5">
                          <div className="flex items-center gap-4">
                            {/* Rank + Avatar */}
                            <div className="flex items-center gap-3 shrink-0">
                              <span className={`text-xs font-bold w-5 text-center ${isTop ? "text-orange-500" : "text-slate-400"}`}>
                                #{index + 1}
                              </span>
                              <div className={`h-10 w-10 rounded-full flex items-center justify-center text-sm font-black text-white ${
                                isTop ? "bg-gradient-to-br from-orange-500 to-orange-600" : "bg-[#1E3A5F]"
                              }`}>
                                {initials}
                              </div>
                            </div>

                            {/* Info */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap">
                                <h3 className="font-bold text-slate-900 text-sm">{candidate.name}</h3>
                                {isTop && (
                                  <Badge className="bg-orange-100 text-orange-700 border-none text-[9px] px-1.5 flex items-center gap-0.5">
                                    <Star className="h-2.5 w-2.5" /> Best Match
                                  </Badge>
                                )}
                                <Badge className={`text-[9px] border-none px-1.5 ${STATUS_COLORS[candidate.status]}`}>
                                  {STATUS_LABELS[candidate.status]}
                                </Badge>
                              </div>
                              <p className="text-xs text-slate-400 mt-0.5 truncate">{candidate.email}</p>
                              <div className="flex flex-wrap gap-1 mt-2">
                                {candidate.matched_skills.slice(0, 4).map((s) => (
                                  <Badge key={s} className="bg-green-50 text-green-700 border-green-200/50 text-[9px] px-1.5 py-0">
                                    {s}
                                  </Badge>
                                ))}
                                {candidate.missing_skills.slice(0, 2).map((s) => (
                                  <Badge key={s} variant="outline" className="text-slate-400 border-slate-200 text-[9px] px-1.5 py-0 line-through">
                                    {s}
                                  </Badge>
                                ))}
                              </div>
                            </div>

                            {/* Score + Actions */}
                            <div className="flex items-center gap-4 shrink-0">
                              <div className="hidden md:flex flex-col gap-1.5 items-end">
                                {/* Composite Score (primary ranking score) */}
                                <div className="text-center">
                                  <p className={`text-2xl font-black ${scoreColor(candidate.composite_score ?? candidate.match_score)}`}>
                                    {(candidate.composite_score ?? candidate.match_score).toFixed(0)}%
                                  </p>
                                  <p className="text-[9px] font-bold uppercase text-slate-400">Overall</p>
                                  <div className="w-16 h-1.5 rounded-full bg-slate-100 mt-1 overflow-hidden">
                                    <div
                                      className={`h-full rounded-full ${scoreBg(candidate.composite_score ?? candidate.match_score)}`}
                                      style={{ width: `${candidate.composite_score ?? candidate.match_score}%` }}
                                    />
                                  </div>
                                </div>
                                {/* Sub-scores */}
                                <div className="flex gap-2 text-[9px] text-slate-400 font-medium">
                                  <span>Skills: <span className="text-slate-700">{candidate.match_score}%</span></span>
                                  <span>Exp: <span className="text-slate-700">{(candidate.experience_score ?? 100).toFixed(0)}%</span></span>
                                </div>
                              </div>

                              <div className="flex flex-col gap-1.5">
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="h-8 px-3 text-slate-600 hover:text-[#1E3A5F] border border-slate-200"
                                  onClick={() => { setSelectedCandidate(candidate); setDetailOpen(true); }}
                                >
                                  <Eye className="h-3.5 w-3.5 mr-1" /> View
                                </Button>
                                {candidate.status !== "shortlisted" ? (
                                  <Button
                                    size="sm"
                                    disabled={isUpdating}
                                    onClick={() => handleStatusUpdate(candidate, "shortlisted")}
                                    className="h-8 px-3 bg-green-500 hover:bg-green-600 text-white text-xs font-semibold"
                                  >
                                    {isUpdating ? <Loader2 className="h-3 w-3 animate-spin" /> : <><CheckCircle2 className="h-3 w-3 mr-1" />Shortlist</>}
                                  </Button>
                                ) : (
                                  <Button
                                    size="sm"
                                    disabled={isUpdating}
                                    onClick={() => handleStatusUpdate(candidate, "rejected")}
                                    className="h-8 px-3 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 text-xs font-semibold"
                                  >
                                    {isUpdating ? <Loader2 className="h-3 w-3 animate-spin" /> : <><XCircle className="h-3 w-3 mr-1" />Reject</>}
                                  </Button>
                                )}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Detail Modal */}
      {selectedCandidate && (
        <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
          <DialogContent className="max-w-lg border-slate-200 shadow-2xl p-0 overflow-hidden">
            <div className="h-1.5 bg-gradient-to-r from-[#F97316] to-[#1E3A5F]" />
            <div className="p-6 space-y-5">
              <DialogHeader>
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-[#1E3A5F] flex items-center justify-center text-white font-black text-lg">
                    {getInitials(selectedCandidate.name)}
                  </div>
                  <div>
                    <DialogTitle className="text-xl font-black text-slate-900">{selectedCandidate.name}</DialogTitle>
                    <DialogDescription className="text-xs text-slate-400">{selectedCandidate.email}</DialogDescription>
                  </div>
                </div>
              </DialogHeader>

              {/* Score */}
              <div className="flex items-center gap-4 p-4 bg-slate-50 rounded-xl">
                <div className="text-center">
                  <p className={`text-3xl font-black ${scoreColor(selectedCandidate.match_score)}`}>
                    {selectedCandidate.match_score}%
                  </p>
                  <p className="text-[10px] font-bold uppercase text-slate-400">Match Score</p>
                </div>
                <div className="flex-1 space-y-1.5">
                  <div className="flex justify-between text-xs text-slate-500">
                    <span>Match Progress</span><span>{selectedCandidate.match_score}%</span>
                  </div>
                  <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${scoreBg(selectedCandidate.match_score)}`}
                      style={{ width: `${selectedCandidate.match_score}%` }}
                    />
                  </div>
                  <p className="text-[10px] text-slate-400">{selectedCandidate.experience_years}+ years experience</p>
                </div>
              </div>

              {/* Skills */}
              <div className="space-y-3">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">Matched Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedCandidate.matched_skills.length > 0
                      ? selectedCandidate.matched_skills.map((s) => (
                          <Badge key={s} className="bg-green-100 text-green-700 border-none">{s}</Badge>
                        ))
                      : <span className="text-xs text-slate-400">None matched</span>}
                  </div>
                </div>
                {selectedCandidate.missing_skills.length > 0 && (
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">Missing Skills</p>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedCandidate.missing_skills.map((s) => (
                        <Badge key={s} variant="outline" className="text-slate-400 border-slate-200 line-through">{s}</Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-2 border-t border-slate-100">
                <Button
                  className="flex-1 bg-green-500 hover:bg-green-600 text-white font-semibold"
                  disabled={selectedCandidate.status === "shortlisted" || updatingStatus === selectedCandidate.application_id}
                  onClick={() => handleStatusUpdate(selectedCandidate, "shortlisted")}
                >
                  <CheckCircle2 className="h-4 w-4 mr-1.5" />
                  {selectedCandidate.status === "shortlisted" ? "Shortlisted ✓" : "Shortlist"}
                </Button>
                <Button
                  className="flex-1 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 font-semibold"
                  disabled={selectedCandidate.status === "rejected" || updatingStatus === selectedCandidate.application_id}
                  onClick={() => handleStatusUpdate(selectedCandidate, "rejected")}
                >
                  <XCircle className="h-4 w-4 mr-1.5" />
                  {selectedCandidate.status === "rejected" ? "Rejected ✓" : "Reject"}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
