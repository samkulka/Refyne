"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { UploadCloud, FileText, Download, Sparkles, Users } from "lucide-react";
import Link from "next/link";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [fileId, setFileId] = useState<string | null>(null);
  const [profile, setProfile] = useState<any>(null);
  const [cleaning, setCleaning] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      // Upload file
      const uploadRes = await apiClient.uploadFile(file);
      setFileId(uploadRes.file_id);

      // Profile file
      const profileRes = await apiClient.profileFile(uploadRes.file_id);
      setProfile(profileRes);

      setUploading(false);
    } catch (err: any) {
      setError(err.message || "Failed to upload file");
      setUploading(false);
    }
  };

  const handleClean = async () => {
    if (!fileId) return;

    setCleaning(true);
    setError(null);

    try {
      // Start cleaning job
      const cleanRes = await apiClient.cleanFile(fileId, { aggressive: false });
      setJobId(cleanRes.job_id);

      // Poll for job status
      const pollInterval = setInterval(async () => {
        try {
          const status = await apiClient.getJobStatus(cleanRes.job_id);
          setJobStatus(status);

          if (status.status === 'completed') {
            clearInterval(pollInterval);
            setCleaning(false);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setCleaning(false);
            setError(status.error || 'Cleaning failed');
          }
        } catch (err: any) {
          clearInterval(pollInterval);
          setCleaning(false);
          setError(err.message || 'Failed to check job status');
        }
      }, 1000); // Poll every second

    } catch (err: any) {
      setError(err.message || "Failed to clean file");
      setCleaning(false);
    }
  };

  const handleDownload = async () => {
    if (!jobId || jobStatus?.status !== 'completed') return;

    try {
      const blob = await apiClient.downloadCleanedFile(jobId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `cleaned_${file?.name || "data.csv"}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.message || "Failed to download file");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <div className="container mx-auto py-12 px-4 max-w-4xl">
        <div className="mb-12 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 text-slate-900">
            Upload Your Data
          </h1>
          <p className="text-2xl text-slate-700 max-w-2xl mx-auto font-medium">
            Get instant AI-powered insights
          </p>
        </div>

        {error && (
          <Card className="mb-6 border-red-500">
            <CardContent className="pt-6">
              <p className="text-red-600">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Upload Section */}
        <Card className="mb-8 border-2 border-slate-200 shadow-xl">
          <CardContent className="pt-12 pb-12">
            <div className="text-center mb-8">
              <div className="inline-flex h-20 w-20 bg-purple-100 rounded-full items-center justify-center mb-4">
                <UploadCloud className="h-10 w-10 text-purple-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Choose a file to analyze</h2>
              <p className="text-lg text-slate-700">
                CSV, Excel, JSON, or Parquet
              </p>
            </div>
            <div className="max-w-md mx-auto">
              <input
                type="file"
                accept=".csv,.xlsx,.xls,.json,.parquet"
                onChange={handleFileChange}
                className="w-full mb-4 text-base file:mr-4 file:py-3 file:px-6 file:rounded-lg file:border-0 file:text-base file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100 file:cursor-pointer"
                disabled={uploading}
              />
              {file && (
                <p className="text-base text-slate-700 mb-4 font-medium">
                  Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
                </p>
              )}
              <Button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white py-6 text-lg font-semibold"
                size="lg"
              >
                {uploading ? "Analyzing..." : "Analyze File"}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Profile Results */}
        {profile && (
          <Card className="mb-8 border-2 border-slate-200 shadow-xl">
            <CardContent className="pt-10 pb-10">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-slate-900 mb-4">File Analysis Complete</h2>
                <div className="inline-flex items-center gap-3 bg-green-50 px-6 py-3 rounded-full">
                  <div className="h-3 w-3 bg-green-500 rounded-full"></div>
                  <span className="text-xl font-bold text-green-700">{Math.round(profile.quality_score)}% Quality</span>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                <div className="text-center">
                  <p className="text-lg text-slate-700 mb-2">Rows</p>
                  <p className="text-4xl font-bold text-slate-900">{profile.total_rows.toLocaleString()}</p>
                </div>
                <div className="text-center">
                  <p className="text-lg text-slate-700 mb-2">Columns</p>
                  <p className="text-4xl font-bold text-slate-900">{profile.total_columns}</p>
                </div>
                <div className="text-center">
                  <p className="text-lg text-slate-700 mb-2">Duplicates</p>
                  <p className="text-4xl font-bold text-slate-900">{profile.duplicate_rows}</p>
                </div>
                <div className="text-center">
                  <p className="text-lg text-slate-700 mb-2">Size</p>
                  <p className="text-4xl font-bold text-slate-900">{profile.memory_usage_mb.toFixed(1)}<span className="text-2xl">MB</span></p>
                </div>
              </div>

              <div className="max-w-md mx-auto">
                <Link href={`/customers/${fileId}`} className="block mb-3">
                  <Button className="w-full bg-purple-600 hover:bg-purple-700 text-white py-6 text-lg font-semibold" size="lg">
                    <Users className="h-6 w-6 mr-2" />
                    View Customer Insights
                  </Button>
                </Link>
                <p className="text-center text-sm text-slate-600">
                  Note: Files are stored temporarily and may be lost on server restarts
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Clean Results */}
        {jobStatus?.status === 'completed' && (
          <Card className="border-2 border-green-200 hover:shadow-lg transition-all">
            <CardHeader>
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center mb-2">
                <Download className="h-6 w-6 text-green-600" />
              </div>
              <CardTitle className="text-slate-900">Cleaned Data Ready</CardTitle>
              <CardDescription className="text-slate-600">
                Cleaning completed successfully
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <p className="text-sm text-slate-600">Job ID: {jobId}</p>
                {jobStatus.completed_at && (
                  <p className="text-sm text-slate-600">
                    Completed: {new Date(jobStatus.completed_at).toLocaleString()}
                  </p>
                )}
              </div>
              <Button onClick={handleDownload} className="w-full bg-green-600 hover:bg-green-700">
                <Download className="h-4 w-4 mr-2" />
                Download Cleaned File
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
