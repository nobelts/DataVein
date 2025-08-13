const API_BASE_URL = 'http://localhost:8000';

export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UploadInitRequest {
  filename: string;
  file_size: number;
}

export interface UploadInitResponse {
  upload_id: string;
  presigned_url: string;
  s3_key: string;
}

export interface UploadResponse {
  id: string;
  filename: string;
  file_size: number;
  status: string;
  created_at: string;
  completed_at?: string;
}

export interface Pipeline {
  id: string;
  upload_id: string;
  status: string;
  config?: any;
  created_at: string;
  completed_at?: string;
}

export interface PipelineConfig {
  synthetic_multiplier?: number;
  include_nulls?: boolean;
}

export interface PipelineCreateRequest {
  upload_id: string;
  config?: PipelineConfig;
}

export interface PipelineResponse {
  id: string;
  upload_id: string;
  status: string;
  config?: any;
  created_at: string;
  completed_at?: string;
}

class ApiClient {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`API Error: ${response.status} - ${errorData}`);
    }

    return response.json();
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    return this.request<TokenResponse>('/auth/token', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async register(userData: RegisterRequest): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // File uploads
  async initUpload(request: UploadInitRequest): Promise<UploadInitResponse> {
    return this.request<UploadInitResponse>('/uploads/init', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async completeUpload(uploadId: string): Promise<void> {
    return this.request<void>(`/uploads/${uploadId}/complete`, {
      method: 'POST',
    });
  }

  async getUploads(): Promise<UploadResponse[]> {
    return this.request<UploadResponse[]>('/uploads/');
  }

  async uploadToS3(presignedUrl: string, file: File): Promise<void> {
    const response = await fetch(presignedUrl, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type,
      },
    });

    if (!response.ok) {
      throw new Error(`S3 Upload failed: ${response.status}`);
    }
  }

  // Pipeline management
  async startPipeline(request: PipelineCreateRequest): Promise<PipelineResponse> {
    return this.request<PipelineResponse>('/pipeline/start', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getPipeline(pipelineId: string): Promise<PipelineResponse> {
    return this.request<PipelineResponse>(`/pipeline/${pipelineId}`);
  }

  async getUserPipelines(): Promise<PipelineResponse[]> {
    return this.request<PipelineResponse[]>('/pipeline/');
  }

  async getPipelines(): Promise<Pipeline[]> {
    return this.request<Pipeline[]>('/pipeline/');
  }

  async checkHealth(): Promise<{ status: string; message: string }> {
    return this.request<{ status: string; message: string }>('/health');
  }
}

export const apiClient = new ApiClient();
