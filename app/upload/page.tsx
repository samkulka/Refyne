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
        <div className="mb-8 text-center">
          <div className="inline-flex items-center gap-2 bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Sparkles className="h-4 w-4" />
            AI-Powered Data Processing
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-slate-900 via-purple-900 to-slate-900 bg-clip-text text-transparent">
            Refyne Data Cleanser
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Upload, profile, and clean your customer data instantly
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
      <Card className="mb-6 border-2 hover:border-purple-200 transition-all hover:shadow-lg">
        <CardHeader>
          <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center mb-2">
            <UploadCloud className="h-6 w-6 text-purple-600" />
          </div>
          <CardTitle className="text-slate-900">Upload File</CardTitle>
          <CardDescription className="text-slate-600">
            Upload a CSV, Excel, JSON, or Parquet file
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <input
              type="file"
              accept=".csv,.xlsx,.xls,.json,.parquet"
              onChange={handleFileChange}
              className="flex-1"
              disabled={uploading}
            />
            <Button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="bg-purple-600 hover:bg-purple-700"
            >
              {uploading ? "Uploading..." : "Upload & Profile"}
            </Button>
          </div>
          {file && (
            <p className="text-sm text-muted-foreground mt-2">
              Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
            </p>
          )}
        </CardContent>
      </Card>

      {/* Profile Results */}
      {profile && (
        <Card className="mb-6 border-2 hover:border-blue-200 transition-all hover:shadow-lg">
          <CardHeader>
            <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mb-2">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <CardTitle className="text-slate-900">Data Profile</CardTitle>
            <CardDescription className="text-slate-600">
              Quality analysis of your uploaded file
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Overall Quality</span>
                  <Badge>{Math.round(profile.quality_score)}%</Badge>
                </div>
                <Progress value={profile.quality_score} />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-600 font-medium">Rows</p>
                  <p className="text-2xl font-bold text-slate-900">{profile.total_rows}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600 font-medium">Columns</p>
                  <p className="text-2xl font-bold text-slate-900">{profile.total_columns}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600 font-medium">Duplicates</p>
                  <p className="text-2xl font-bold text-slate-900">{profile.duplicate_rows}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600 font-medium">Memory Usage</p>
                  <p className="text-2xl font-bold text-slate-900">{profile.memory_usage_mb.toFixed(2)} MB</p>
                </div>
              </div>

              {profile.issues_summary && Object.keys(profile.issues_summary).length > 0 && (
                <div className="mt-4">
                  <p className="text-sm font-medium mb-2">Issues Found:</p>
                  <ul className="space-y-2">
                    {Object.entries(profile.issues_summary).map(([issue, count], idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm">
                        <Sparkles className="h-4 w-4 mt-0.5 text-blue-500" />
                        {issue.replace(/_/g, ' ')}: {String(count)}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="grid grid-cols-2 gap-3 mt-4">
                <Button
                  onClick={handleClean}
                  disabled={cleaning}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  {cleaning ? `Cleaning... ${jobStatus?.progress || 0}%` : "Clean Data"}
                </Button>
                <Link href={`/customers/${fileId}`}>
                  <Button variant="outline" className="w-full border-purple-200 text-purple-700 hover:bg-purple-50">
                    <Users className="h-4 w-4 mr-2" />
                    View Customers
                  </Button>
                </Link>
              </div>
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
  );
}
