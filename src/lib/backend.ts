import { auth, currentUser } from "@clerk/nextjs/server";

export type PipelineStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";

export type ProjectSummary = {
  id: string;
  title: string;
  prompt: string | null;
  status: string;
  error: string | null;
  createdAt: string;
  updatedAt: string;
  upload: UploadOut | null;
  analysis: JsonRecordOut | null;
  ocrResult: JsonRecordOut | null;
  layerData: JsonRecordOut | null;
  storyboard: JsonRecordOut | null;
  motionPlan: JsonRecordOut | null;
  evaluation: JsonRecordOut | null;
  renders: RenderOut[];
  pipeline: PipelineStepOut[];
  agentLogs: AgentLogOut[];
};

type UploadOut = {
  id: string;
  imageUrl: string;
  fileName: string;
  mimeType: string;
  width: number | null;
  height: number | null;
  size: number;
  createdAt: string;
};

type JsonRecordOut = {
  id: string;
  createdAt: string;
  analysisJson?: unknown;
  ocrJson?: unknown;
  layersJson?: unknown;
  storyboardJson?: unknown;
  motionPlanJson?: unknown;
  evaluationJson?: unknown;
  approved?: boolean;
  warning?: string | null;
};

type RenderOut = {
  id: string;
  videoUrl: string | null;
  format: string;
  renderStatus: string;
  logs: string | null;
  createdAt: string;
  updatedAt: string;
};

type PipelineStepOut = {
  id: string;
  key: string;
  label: string;
  status: PipelineStatus;
  startedAt: string | null;
  endedAt: string | null;
  errorMessage: string | null;
  duration: number | null;
};

type AgentLogOut = {
  id: string;
  agentName: string;
  input: unknown;
  output: unknown;
  createdAt: string;
};

export type DashboardPayload = {
  projects: ProjectSummary[];
  renderCount: number;
  completedCount: number;
};

function backendBaseUrl(): string {
  // Server-side: BACKEND_URL (private, not exposed to browser)
  // Client-side: NEXT_PUBLIC_BACKEND_URL (public, set at build time)
  const url =
    process.env.BACKEND_URL ??
    process.env.NEXT_PUBLIC_BACKEND_URL;

  if (!url) {
    // Fail loudly so a missing env var surfaces immediately rather than
    // silently hitting localhost (which never works in production).
    if (process.env.NODE_ENV === "production") {
      throw new Error(
        "BACKEND_URL (server) or NEXT_PUBLIC_BACKEND_URL (client) is not set. " +
        "Add it to your Vercel environment variables."
      );
    }
    // Local dev convenience fallback only.
    return "http://localhost:8000";
  }

  return url.replace(/\/$/, "");
}

async function authHeaders() {
  const authState = await auth();
  const token = await authState.getToken();
  if (!token) {
    throw new Error("Authentication required.");
  }
  const user = await currentUser();
  const email = user?.emailAddresses.find((address) => address.id === user.primaryEmailAddressId)?.emailAddress;
  return {
    Authorization: `Bearer ${token}`,
    ...(email ? { "X-Clerk-Email": email } : {})
  };
}

async function backendFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = await authHeaders();
  const response = await fetch(`${backendBaseUrl()}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      ...headers,
      ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...init.headers
    }
  });

  if (!response.ok) {
    let detail = `Backend request failed: ${response.status}`;
    const rawBody = await response.text();
    try {
      const body = JSON.parse(rawBody) as { detail?: string };
      detail = body.detail ?? detail;
    } catch {
      detail = rawBody || detail;
    }
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export function getDashboard() {
  return backendFetch<DashboardPayload>("/projects");
}

export function getProject(projectId: string) {
  return backendFetch<ProjectSummary>(`/project/${projectId}`);
}

export function createProject(formData: FormData) {
  return backendFetch<ProjectSummary>("/project/create", {
    method: "POST",
    body: formData
  });
}

export function runPipeline(projectId: string, format: string) {
  return backendFetch<{ project: ProjectSummary; renderId: string | null; queued: boolean }>("/pipeline/run", {
    method: "POST",
    body: JSON.stringify({ projectId, format })
  });
}

export function deleteProject(projectId: string) {
  return backendFetch<{ success: boolean }>(`/project/${projectId}`, {
    method: "DELETE"
  });
}
