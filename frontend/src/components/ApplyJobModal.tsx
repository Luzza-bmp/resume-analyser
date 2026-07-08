import React, { useState, useRef } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Loader2,
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  Briefcase,
  MapPin,
  Clock,
  Sparkles,
  Award,
  AlertTriangle,
  FileText
} from "lucide-react";
import axios from "axios";

interface ApplyJobModalProps {
  isOpen: boolean;
  onClose: () => void;
  job: any;
  applied: boolean;
  onApplySuccess: (jobId: string) => void;
}

const API = "http://localhost:5000/api";

export function ApplyJobModal({ isOpen, onClose, job, applied, onApplySuccess }: ApplyJobModalProps) {
  const [step, setStep] = useState<"details" | "score" | "success">("details");
  const [isScoring, setIsScoring] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [scoreData, setScoreData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!job) return null;

  const formatSalary = () => {
    if (job.salary_min && job.salary_max) return `Rs.${Math.round(job.salary_min)}-${Math.round(job.salary_max)} LPA`;
    if (job.salary_min) return `Rs.${Math.round(job.salary_min)}+ LPA`;
    return null;
  };

  const handleScoreExistingResume = async () => {
    setIsScoring(true);
    setError(null);
    try {
      const token = localStorage.getItem("access_token");
      const res = await axios.post(`${API}/jobs/${job.job_id}/score-resume`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setScoreData(res.data);
      setStep("score");
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.error || "Failed to score existing resume. Please upload a new one.");
    } finally {
      setIsScoring(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsScoring(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = localStorage.getItem("access_token");
      const res = await axios.post(`${API}/jobs/${job.job_id}/score-resume`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data"
        }
      });
      setScoreData(res.data);
      setStep("score");
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.error || "Failed to upload and parse resume.");
    } finally {
      setIsScoring(false);
    }
  };

  const handleFinalApply = async () => {
    if (!scoreData?.resume_id) return;
    setIsApplying(true);
    setError(null);
    try {
      const token = localStorage.getItem("access_token");
      await axios.post(`${API}/jobs/${job.job_id}/apply`, {
        resume_id: scoreData.resume_id
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStep("success");
      onApplySuccess(job.job_id);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.error || "Failed to submit application.");
    } finally {
      setIsApplying(false);
    }
  };

  const handleClose = () => {
    setStep("details");
    setScoreData(null);
    setError(null);
    onClose();
  };

  const scoreColor = (score: number) => {
    if (score >= 75) return "text-green-600 border-green-200 bg-green-50";
    if (score >= 50) return "text-orange-500 border-orange-200 bg-orange-50";
    return "text-slate-500 border-slate-200 bg-slate-50";
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-3xl overflow-y-auto max-h-[90vh] p-0 border-slate-200 shadow-2xl">
        <div className="h-2 bg-gradient-to-r from-blue-700 via-blue-800 to-[#F97316]"></div>
        
        <div className="p-6 md:p-8 space-y-6">
          <DialogHeader>
            <div className="flex justify-between items-start gap-4">
              <div>
                <span className="text-xs font-semibold text-[#F97316] uppercase tracking-wider">Job Match & Application</span>
                <DialogTitle className="text-2xl font-black text-slate-900 mt-1">{job.title}</DialogTitle>
                <p className="text-sm text-slate-500">{job.recruiter_company || job.recruiter_name || "Company"}</p>
              </div>
              {applied && (
                <Badge className="bg-green-100 text-green-700 border-none px-3 py-1 flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3" /> Already Applied
                </Badge>
              )}
            </div>
          </DialogHeader>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2 text-sm">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {step === "details" && (
            <div className="space-y-6 animate-in fade-in duration-300">
              {/* Job Metadata Tags */}
              <div className="flex flex-wrap gap-2.5">
                {job.location && (
                  <div className="flex items-center text-xs text-slate-600 gap-1.5 bg-slate-50 border border-slate-100 px-3 py-1.5 rounded-lg">
                    <MapPin className="h-3.5 w-3.5 text-slate-400" /> {job.location}
                  </div>
                )}
                {job.job_type && (
                  <div className="flex items-center text-xs text-slate-600 gap-1.5 bg-slate-50 border border-slate-100 px-3 py-1.5 rounded-lg">
                    <Clock className="h-3.5 w-3.5 text-slate-400" /> {job.job_type}
                  </div>
                )}
                {formatSalary() && (
                  <div className="flex items-center text-xs text-slate-600 gap-1.5 bg-slate-50 border border-slate-100 px-3 py-1.5 rounded-lg">
                    <Briefcase className="h-3.5 w-3.5 text-slate-400" /> {formatSalary()}
                  </div>
                )}
                {job.experience_level && (
                  <div className="flex items-center text-xs text-slate-600 gap-1.5 bg-slate-50 border border-slate-100 px-3 py-1.5 rounded-lg">
                    Exp: {job.experience_level}
                  </div>
                )}
              </div>

              {/* Description section */}
              <div className="space-y-2">
                <h4 className="font-bold text-slate-800 text-sm">Job Description</h4>
                <div className="p-4 bg-slate-50/50 border border-slate-100 rounded-xl max-h-[180px] overflow-y-auto">
                  <p className="text-slate-600 text-sm leading-relaxed whitespace-pre-wrap">
                    {job.description || "No description provided."}
                  </p>
                </div>
              </div>

              {/* Required Skills */}
              <div className="space-y-2">
                <h4 className="font-bold text-slate-800 text-sm">Required Skills</h4>
                <div className="flex flex-wrap gap-1.5">
                  {job.skills && job.skills.length > 0 ? (
                    job.skills.map((s: string) => (
                      <Badge key={s} variant="secondary" className="bg-slate-100 text-slate-700 hover:bg-slate-100 text-xs px-2.5">
                        {s}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-xs text-slate-400">No specific skills listed.</span>
                  )}
                </div>
              </div>

              {/* Apply / Upload Resume Action Container */}
              {!applied && (
                <div className="pt-4 border-t border-slate-100 flex flex-col gap-3">
                  <p className="text-xs text-slate-500 font-medium">
                    To apply, confirm your resume. The system will calculate your match score before you submit.
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <Button
                      variant="outline"
                      onClick={handleScoreExistingResume}
                      disabled={isScoring}
                      className="border-slate-200 hover:bg-slate-50 py-5"
                    >
                      {isScoring ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : (
                        <FileText className="h-4 w-4 mr-2 text-blue-600" />
                      )}
                      Use Uploaded Resume
                    </Button>
                    <input
                      type="file"
                      ref={fileInputRef}
                      accept=".pdf"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                    <Button
                      className="bg-[#1E3A5F] hover:bg-[#1E3A5F]/90 text-white py-5"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isScoring}
                    >
                      {isScoring ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : (
                        <UploadCloud className="h-4 w-4 mr-2" />
                      )}
                      Upload New PDF
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}

          {step === "score" && scoreData && (
            <div className="space-y-6 animate-in zoom-in-95 duration-300">
              <div className="text-center py-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Evaluation Results</span>
                <h3 className="text-xl font-bold text-slate-900 mt-1">AI Resume Match Fit</h3>
              </div>

              {/* Match Score Display */}
              <div className={`p-6 border rounded-2xl flex flex-col md:flex-row items-center justify-between gap-6 ${scoreColor(scoreData.match_score)}`}>
                <div className="flex items-center gap-4">
                  <div className="h-16 w-16 rounded-full bg-white flex items-center justify-center border-2 border-current shadow-inner shrink-0">
                    <span className="text-2xl font-black">{scoreData.match_score}%</span>
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900">Match Percentage</h4>
                    <p className="text-xs text-slate-600 mt-0.5">Based on required skills overlap</p>
                  </div>
                </div>
                <div className="text-right text-xs text-slate-600 shrink-0 max-w-[220px] md:max-w-[280px]">
                  <p className="font-semibold truncate" title={scoreData.filename}>{scoreData.filename || "Resume.pdf"}</p>
                  <p className="mt-0.5">Experience Extracted: {scoreData.experience_years} Years</p>
                </div>
              </div>

              {/* Skills Overlap Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl space-y-2">
                  <div className="flex items-center gap-1.5 text-green-700 font-bold text-xs uppercase">
                    <CheckCircle2 className="h-4 w-4 text-green-600" /> Matched Skills ({scoreData.matched_skills.length})
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {scoreData.matched_skills.length > 0 ? (
                      scoreData.matched_skills.map((s: string) => (
                        <Badge key={s} className="bg-green-100 text-green-700 hover:bg-green-100 border-none text-[10px]">
                          {s}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400">No matching skills found</span>
                    )}
                  </div>
                </div>

                <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl space-y-2">
                  <div className="flex items-center gap-1.5 text-slate-500 font-bold text-xs uppercase">
                    <AlertTriangle className="h-4 w-4 text-slate-400" /> Missing Skills ({scoreData.missing_skills.length})
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {scoreData.missing_skills.length > 0 ? (
                      scoreData.missing_skills.map((s: string) => (
                        <Badge key={s} variant="outline" className="text-slate-400 border-slate-200 text-[10px] line-through">
                          {s}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-xs text-green-600 font-medium">Matches 100% of skills!</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Decision Section */}
              <div className="pt-4 border-t border-slate-100 flex items-center justify-between gap-4 flex-wrap">
                <Button variant="outline" onClick={() => setStep("details")} className="border-slate-200">
                  Back
                </Button>
                <div className="flex gap-2.5">
                  <Button variant="ghost" onClick={handleClose}>
                    Decide Later
                  </Button>
                  <Button
                    onClick={handleFinalApply}
                    disabled={isApplying}
                    className="bg-[#F97316] hover:bg-[#F97316]/90 text-white font-bold px-6 shadow-md"
                  >
                    {isApplying ? (
                      <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Applying...</>
                    ) : (
                      "Apply For Job"
                    )}
                  </Button>
                </div>
              </div>
            </div>
          )}

          {step === "success" && (
            <div className="text-center py-8 space-y-4 animate-in zoom-in-95 duration-400">
              <div className="h-16 w-16 rounded-full bg-green-50 flex items-center justify-center mx-auto text-green-600 border border-green-200 shadow-md">
                <CheckCircle2 className="h-10 w-10" />
              </div>
              <div className="space-y-1">
                <h3 className="text-2xl font-black text-slate-900">Application Submitted!</h3>
                <p className="text-slate-500 text-sm max-w-sm mx-auto">
                  Your application and match profile have been successfully submitted to the recruiter.
                </p>
              </div>
              <div className="pt-4">
                <Button onClick={handleClose} className="bg-[#1E3A5F] hover:bg-[#1E3A5F]/90 text-white font-bold px-8">
                  Back to Dashboard
                </Button>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
