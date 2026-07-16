import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText, UploadCloud, Loader2, CheckCircle2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import axios from "axios";

const API = "http://localhost:5000/api";

export default function ApplicantResume() {
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [resume, setResume] = useState<any>(null);

  const fetchResume = async () => {
    const userId = localStorage.getItem("user_id");
    if (!userId) { setLoading(false); return; }
    try {
      const res = await axios.get(`${API}/resumes?applicant_id=${userId}`);
      if (res.data.length > 0) {
        setResume(res.data[0]); // latest resume
      }
    } catch (err) {
      console.error("Failed to load resume", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchResume(); }, []);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const userId = localStorage.getItem("user_id");
    if (!userId) {
      toast({ title: "Not logged in", variant: "destructive" });
      return;
    }

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast({ title: "Invalid file", description: "Please upload a PDF file.", variant: "destructive" });
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('applicant_id', userId);

      const res = await axios.post(`${API}/resumes/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      toast({
        title: "Resume uploaded!",
        description: `${res.data.skill_count} skills extracted successfully.`,
      });
      await fetchResume();
    } catch (err: any) {
      toast({
        title: "Upload failed",
        description: err.response?.data?.error || "Failed to upload resume.",
        variant: "destructive"
      });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#1E3A5F]" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">My Resume</h1>
        <p className="text-slate-500 mt-1">Manage your document and extracted skills profile.</p>
      </div>

      {resume ? (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Left Column: PDF Resume Viewer (2/3 width) */}
          <div className="xl:col-span-2 space-y-6">
            <Card className="h-[750px] flex flex-col overflow-hidden shadow-md border-slate-200">
              <CardHeader className="pb-3 border-b border-slate-100 bg-slate-50/50 flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-lg font-bold flex items-center gap-2 text-slate-800">
                    <FileText className="h-5 w-5 text-red-500" /> Resume Document Preview
                  </CardTitle>
                  <CardDescription className="truncate max-w-[400px]">
                    {resume.file_path || "Active Resume"}
                  </CardDescription>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <span className="text-xs text-green-600 font-semibold bg-green-50 px-2 py-1 rounded-md border border-green-200">Active</span>
                </div>
              </CardHeader>
              <CardContent className="p-0 flex-1 bg-slate-100">
                <iframe
                  src={`${API}/resumes/download/${resume.file_path}#toolbar=0`}
                  className="w-full h-full border-none"
                  title="Resume PDF Preview"
                />
              </CardContent>
            </Card>
          </div>

          {/* Right Column: AI Extraction & Details (1/3 width) */}
          <div className="xl:col-span-1 space-y-6 flex flex-col">
            {/* Extracted Profile Card */}
            <Card className="flex-1 flex flex-col border-slate-200 shadow-sm">
              <CardHeader className="pb-2 border-b border-slate-100">
                <div>
                  <CardTitle className="text-base font-bold">Extracted Profile</CardTitle>
                  <CardDescription>AI-extracted skills & metadata.</CardDescription>
                </div>
              </CardHeader>
              <CardContent className="pt-6 flex-1 space-y-6">
                {resume.skills.length > 0 ? (
                  <div className="space-y-6">
                    <div>
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Extracted Skills ({resume.skills.length})</h4>
                      <div className="flex flex-wrap gap-1.5">
                        {resume.skills.map((skill: string, i: number) => (
                          <Badge
                            key={skill}
                            className={i < 4
                              ? "bg-[#1E3A5F] hover:bg-[#1E3A5F]/90 text-white px-2.5 py-0.5 text-xs font-semibold"
                              : "bg-slate-100 text-slate-700 hover:bg-slate-200 px-2.5 py-0.5 text-xs font-normal"
                            }
                          >
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="pt-5 border-t border-slate-100">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Document Details</h4>
                      <div className="space-y-2.5 text-xs text-slate-600">
                        <p className="flex justify-between">
                          <span className="font-semibold text-slate-500">File Name:</span>
                          <span className="font-medium text-slate-800 truncate max-w-[200px]" title={resume.file_path}>{resume.file_path || "Resume.pdf"}</span>
                        </p>
                        <p className="flex justify-between">
                          <span className="font-semibold text-slate-500">Uploaded On:</span>
                          <span className="font-medium text-slate-800">
                            {new Date(resume.uploaded_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                          </span>
                        </p>
                        <p className="flex justify-between">
                          <span className="font-semibold text-slate-500">Experience Extracted:</span>
                          <span className="font-medium text-slate-800">{resume.experience_years || 0} Years</span>
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-6 text-slate-400 text-xs">
                    No skills extracted yet.
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Replace / Upload Actions Card */}
            <Card className="border-slate-200 shadow-sm shrink-0">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-bold">Replace Document</CardTitle>
                <CardDescription>Upload a new PDF to update your profile.</CardDescription>
              </CardHeader>
              <CardContent>
                <div
                  className="border-2 border-dashed border-slate-200 hover:border-blue-500/70 hover:bg-slate-50 rounded-xl p-6 flex flex-col items-center justify-center text-center transition-colors cursor-pointer group"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="h-10 w-10 rounded-full bg-blue-50 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
                    {uploading ? (
                      <Loader2 className="h-5 w-5 text-[#1E3A5F] animate-spin" />
                    ) : (
                      <UploadCloud className="h-5 w-5 text-[#1E3A5F]" />
                    )}
                  </div>
                  <h4 className="font-bold text-slate-800 text-xs">
                    {uploading ? "Analyzing new document..." : "Click to Replace"}
                  </h4>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf"
                    className="hidden"
                    onChange={handleFileSelect}
                    disabled={uploading}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      ) : (
        <div className="max-w-xl mx-auto space-y-6">
          <Card className="border-slate-200 shadow-md">
            <CardHeader className="text-center">
              <CardTitle>Upload your resume</CardTitle>
              <CardDescription>We will automatically extract your skills to match you with top job opportunities.</CardDescription>
            </CardHeader>
            <CardContent>
              <div
                className="border-2 border-dashed border-slate-200 rounded-xl p-12 flex flex-col items-center justify-center text-center bg-slate-50/50 hover:bg-slate-50 transition-colors cursor-pointer group"
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="h-14 w-14 rounded-full bg-blue-50 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  {uploading ? (
                    <Loader2 className="h-7 w-7 text-[#1E3A5F] animate-spin" />
                  ) : (
                    <UploadCloud className="h-7 w-7 text-[#1E3A5F]" />
                  )}
                </div>
                <h4 className="font-bold text-slate-900 text-sm">
                  {uploading ? "Analyzing resume..." : "Upload Resume PDF"}
                </h4>
                <p className="text-xs text-slate-500 mt-2 max-w-xs">
                  {uploading ? "Extracting skills and building your profile..." : "Drag and drop your PDF file here, or click to browse."}
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  className="hidden"
                  onChange={handleFileSelect}
                  disabled={uploading}
                />
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
