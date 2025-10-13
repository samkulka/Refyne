// Refyne API Client
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

export interface UploadResponse {
  success: boolean;
  file_id: string;
  filename: string;
  size_bytes: number;
  message: string;
}

export interface ProfileResponse {
  total_rows: number;
  total_columns: number;
  duplicate_rows: number;
  memory_usage_mb: number;
  quality_score: number;
  issues_summary: {
    [key: string]: number;
  };
  column_details?: Array<{
    name: string;
    type: string;
    dtype: string;
    null_percentage: number;
    unique_count: number;
    issues: string[];
  }>;
}

export interface CleanResponse {
  job_id: string;
  status: string;
  created_at: string;
  message: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error?: string;
  result_file_id?: string;
}

class RefyneAPIClient {
  private baseURL: string;
  private apiKey: string;

  constructor() {
    this.baseURL = API_URL;
    this.apiKey = API_KEY;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}/api/v1${endpoint}`;
    const headers = {
      'X-API-Key': this.apiKey,
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async health() {
    return this.request('/health');
  }

  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request('/upload', {
      method: 'POST',
      body: formData,
      headers: {},  // Let browser set Content-Type for multipart
    });
  }

  async profileFile(fileId: string): Promise<ProfileResponse> {
    return this.request('/profile', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ file_id: fileId }),
    });
  }

  async cleanFile(
    fileId: string,
    options: { aggressive?: boolean } = {}
  ): Promise<CleanResponse> {
    return this.request('/clean', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_id: fileId,
        mode: options.aggressive ? 'aggressive' : 'standard',
      }),
    });
  }

  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    return this.request(`/jobs/${jobId}`);
  }

  async downloadCleanedFile(jobId: string): Promise<Blob> {
    const url = `${this.baseURL}/api/v1/jobs/${jobId}/download`;
    const response = await fetch(url, {
      headers: {
        'X-API-Key': this.apiKey,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to download file: ${response.statusText}`);
    }

    return response.blob();
  }

  async downloadFile(fileId: string): Promise<Blob> {
    const url = `${this.baseURL}/api/v1/download/${fileId}`;
    const response = await fetch(url, {
      headers: {
        'X-API-Key': this.apiKey,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to download file: ${response.statusText}`);
    }

    return response.blob();
  }
}

export const apiClient = new RefyneAPIClient();
