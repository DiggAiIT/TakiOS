/**
 * Type-safe API client for TakiOS backend.
 */

const DEFAULT_API_URL = "http://localhost:8000/api/v1";

function normalizeApiUrl(value: string | undefined): string {
  const rawValue = value?.trim();
  if (!rawValue) {
    return DEFAULT_API_URL;
  }
  return rawValue.endsWith("/") ? rawValue.slice(0, -1) : rawValue;
}

const API_URL = normalizeApiUrl(process.env.NEXT_PUBLIC_API_URL);

interface RequestOptions extends RequestInit {
  token?: string;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { token, ...fetchOptions } = options;
  const isFormDataBody = typeof FormData !== "undefined" && fetchOptions.body instanceof FormData;
  const headers: Record<string, string> = {
    ...((options.headers as Record<string, string> | undefined) ?? {}),
  };
  if (!isFormDataBody && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(response.status, error.detail || "Request failed");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export { API_URL };

// ── Type definitions ────────────────────────────────────────────────

export interface UserData {
  id: string;
  email: string;
  full_name: string;
  role: string;
  locale: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface SubjectData {
  id: string;
  name_de: string;
  name_en: string;
  description_de: string;
  description_en: string;
  department: string;
}

export interface ModuleData {
  id: string;
  subject_id: string;
  code: string;
  name_de: string;
  name_en: string;
  semester: number;
  credits: number;
  description_de: string;
  description_en: string;
}

export interface ModuleUnitData {
  id: string;
  position: number;
  title_de: string;
  title_en: string;
}

export interface ModuleDetailData extends ModuleData {
  units: ModuleUnitData[];
}

export interface MnemonicData {
  id: string;
  content_id: string;
  mnemonic_text: string;
  mnemonic_type: "acronym" | "story" | "visual" | "rhyme" | "analogy";
  language: string;
  ai_generated: boolean;
  effectiveness_score: number | null;
}

export interface ContentWithBodyData {
  id: string;
  module_unit_id: string;
  body_markdown: string;
  mnemonics: MnemonicData[];
}

export interface ExamData {
  id: string;
  module_id: string;
  title: string;
  exam_type: "digital" | "pen_and_paper" | "hybrid";
  time_limit_minutes: number | null;
}

export interface QuestionData {
  id: string;
  question_type: "multiple_choice" | "free_text" | "diagram_label" | "matching";
  question_de: string;
  question_en: string;
  answer_options: { options?: string[]; pairs?: Array<{ left: string; right: string }> } | null;
  difficulty: "easy" | "medium" | "hard";
  bloom_level: string;
}

export interface StartExamData {
  attempt_id: string;
  questions: QuestionData[];
}

export interface ExamResultData {
  attempt_id: string;
  total_score: number | null;
  passed: boolean | null;
  answers: Array<Record<string, unknown>>;
}

export interface LearningPhaseData {
  phase_number: number;
  title_de: string;
  title_en: string;
  semester_equivalent: number;
  module_codes: string[];
  module_names: string[];
  project_relevance: string;
}

export interface ProjectAnalysisData {
  complexity_level: string;
  complexity_name_de: string;
  complexity_name_en: string;
  reasoning: string;
  required_module_codes: string[];
  required_module_names: string[];
  total_credits: number;
  learning_path: LearningPhaseData[];
  suggested_milestones: Array<{ title: string; description: string }>;
  project_context: Record<string, string>;
}

// ── L01: Knowledge Pyramid ──────────────────────────────────────────

export type LevelStatus = "locked" | "in_progress" | "completed";

export interface KnowledgeLevelData {
  id: string;
  parent_id: string | null;
  name_de: string;
  name_en: string;
  description_de: string;
  description_en: string;
  pyramid_position: number;
  icon_url: string | null;
  unlock_criteria: { required_module_codes?: string[] } | null;
}

export interface PyramidData {
  levels: KnowledgeLevelData[];
  progress: Record<string, LevelStatus>;
}

// ── L02: Tech Units ─────────────────────────────────────────────────

export interface TechUnitData {
  id: string;
  level_id: string;
  name_de: string;
  name_en: string;
  description_de: string;
  description_en: string;
  io_spec: { input: string; output: string } | null;
  limitations: string;
}

export interface TechUnitChainData {
  id: string;
  name: string;
  level_id: string;
  description: string;
  units: TechUnitData[];
}

// ── Auth ────────────────────────────────────────────────────────────

export const auth = {
  register: (data: { email: string; password: string; full_name: string; role?: string; locale?: string }) =>
    request<UserData>("/auth/register", { method: "POST", body: JSON.stringify(data) }),

  login: (email: string, password: string) =>
    request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: (token: string) => request<UserData>("/auth/me", { token }),
};

// ── Project Analyzer ─────────────────────────────────────────────

export const analyzer = {
  analyze: (data: { idea: string; use_ai?: boolean }) =>
    request<ProjectAnalysisData>("/analyzer/analyze", {
      method: "POST",
      body: JSON.stringify({ ...data, use_ai: data.use_ai ?? true }),
    }),
};

// ── Levels (L01) ────────────────────────────────────────────────────

export const levels = {
  list: (token: string) => request<KnowledgeLevelData[]>("/levels/", { token }),
  pyramid: (token: string) => request<PyramidData>("/levels/pyramid", { token }),
};

// ── Tech Units (L02) ────────────────────────────────────────────────

export const techUnits = {
  list: (token: string, levelId?: string) => {
    const params = levelId ? `?level_id=${levelId}` : "";
    return request<TechUnitData[]>(`/tech-units/${params}`, { token });
  },
  chains: (levelId: string, token: string) =>
    request<TechUnitChainData[]>(`/tech-units/chains?level_id=${levelId}`, { token }),
};

// ── Subjects & Modules (L03) ────────────────────────────────────────

export const subjects = {
  list: (token: string) => request<SubjectData[]>("/subjects/", { token }),
  modules: (subjectId: string, token: string) =>
    request<ModuleData[]>(`/subjects/${subjectId}/modules`, { token }),
  allModules: (token: string, semester?: number) => {
    const params = semester ? `?semester=${semester}` : "";
    return request<ModuleData[]>(`/subjects/modules${params}`, { token });
  },
  moduleDetail: (moduleId: string, token: string) =>
    request<ModuleDetailData>(`/subjects/modules/${moduleId}`, { token }),
};

// ── Content (L04) ───────────────────────────────────────────────────

export const content = {
  getForUnit: (unitId: string, token: string) =>
    request<ContentWithBodyData>(`/content/unit/${unitId}`, { token }),

  getMnemonics: (unitId: string, token: string) =>
    request<MnemonicData[]>(`/content/unit/${unitId}/mnemonics`, { token }),

  generateMnemonic: (
    data: { content_id: string; mnemonic_type: string; language: string },
    token: string
  ) =>
    request<MnemonicData>("/content/mnemonics/generate", {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),

  rateMnemonic: (mnemonicId: string, score: number, token: string) =>
    request<MnemonicData>(`/content/mnemonics/${mnemonicId}/rate`, {
      method: "POST",
      body: JSON.stringify({ score }),
      token,
    }),
};

// ── Assessments (L05) ───────────────────────────────────────────────

export const assessments = {
  list: (moduleId: string, token: string) =>
    request<ExamData[]>(`/assessment/exams?module_id=${moduleId}`, { token }),

  start: (examId: string, token: string) =>
    request<StartExamData>(`/assessment/exams/${examId}/start`, { method: "POST", token }),

  submit: (
    attemptId: string,
    data: { answers: Array<{ question_id: string; answer_data: Record<string, unknown> }> },
    token: string
  ) =>
    request<ExamResultData>(`/assessment/attempts/${attemptId}/submit`, {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),
};

// ── L06: Projects ──────────────────────────────────────────────────

export type ProjectStatus = "draft" | "active" | "review" | "completed" | "archived";
export type RealizationStage = "idea" | "concept" | "mvp" | "2d" | "3d" | "real_world" | "lifecycle";

export interface ProjectData {
  id: string;
  title: string;
  description: string;
  created_by: string;
  module_id: string | null;
  realization_stage: RealizationStage;
  status: ProjectStatus;
}

export interface MilestoneData {
  id: string;
  title: string;
  description: string;
  position: number;
  completed: boolean;
}

export interface ArtifactData {
  id: string;
  project_id: string;
  file_url: string;
  file_type: string;
  uploaded_by: string;
  created_at: string;
}

export interface ProjectDetailData extends ProjectData {
  milestones: MilestoneData[];
  artifacts: ArtifactData[];
}

export const projects = {
  list: (token: string) => request<ProjectData[]>("/projects/", { token }),

  create: (data: { title: string; description: string; module_id?: string }, token: string) =>
    request<ProjectData>("/projects/", { method: "POST", body: JSON.stringify(data), token }),

  get: (id: string, token: string) => request<ProjectDetailData>(`/projects/${id}`, { token }),

  update: (
    id: string,
    data: { title?: string; description?: string; status?: ProjectStatus; realization_stage?: RealizationStage },
    token: string
  ) =>
    request<ProjectData>(`/projects/${id}`, { method: "PATCH", body: JSON.stringify(data), token }),

  addMilestone: (projectId: string, data: { title: string; description?: string }, token: string) =>
    request<MilestoneData>(`/projects/${projectId}/milestones`, {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),

  updateMilestone: (
    milestoneId: string,
    data: { title?: string; description?: string; completed?: boolean },
    token: string
  ) =>
    request<MilestoneData>(`/projects/milestones/${milestoneId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
      token,
    }),

  deleteMilestone: (milestoneId: string, token: string) =>
    request<void>(`/projects/milestones/${milestoneId}`, { method: "DELETE", token }),

  uploadArtifact: (projectId: string, file: File, token: string) => {
    const body = new FormData();
    body.append("file", file);

    return request<ArtifactData>(`/projects/${projectId}/artifacts`, {
      method: "POST",
      body,
      token,
    });
  },
};

// ── L07: Faculty Collaboration ─────────────────────────────────────

export type ReviewStatus = "pending" | "accepted" | "completed" | "declined";

export interface FacultyProfileData {
  id: string;
  user_id: string;
  department: string;
  expertise_areas: { areas?: string[] } | null;
  available_for_review: boolean;
}

export interface ReviewRequestData {
  id: string;
  project_id: string;
  faculty_id: string;
  requested_by: string;
  status: ReviewStatus;
  review_text: string | null;
  created_at: string;
}

export const collaboration = {
  listFaculty: (token: string) =>
    request<FacultyProfileData[]>("/collaboration/faculty", { token }),

  getMyProfile: (token: string) =>
    request<FacultyProfileData>("/collaboration/faculty/profile", { token }),

  createProfile: (data: { department: string; expertise_areas: string[] }, token: string) =>
    request<FacultyProfileData>("/collaboration/faculty/profile", {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),

  updateProfile: (
    data: { department?: string; expertise_areas?: string[]; available_for_review?: boolean },
    token: string
  ) =>
    request<FacultyProfileData>("/collaboration/faculty/profile", {
      method: "PATCH",
      body: JSON.stringify(data),
      token,
    }),

  requestReview: (data: { project_id: string; faculty_id: string }, token: string) =>
    request<ReviewRequestData>("/collaboration/reviews", {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),

  incomingReviews: (token: string) =>
    request<ReviewRequestData[]>("/collaboration/reviews/incoming", { token }),

  projectReviews: (projectId: string, token: string) =>
    request<ReviewRequestData[]>(`/collaboration/reviews/project/${projectId}`, { token }),

  acceptReview: (reviewId: string, token: string) =>
    request<ReviewRequestData>(`/collaboration/reviews/${reviewId}/accept`, {
      method: "POST",
      token,
    }),

  declineReview: (reviewId: string, token: string) =>
    request<ReviewRequestData>(`/collaboration/reviews/${reviewId}/decline`, {
      method: "POST",
      token,
    }),

  completeReview: (reviewId: string, reviewText: string, token: string) =>
    request<ReviewRequestData>(`/collaboration/reviews/${reviewId}/complete`, {
      method: "POST",
      body: JSON.stringify({ review_text: reviewText }),
      token,
    }),
};

// ── L11: Legal Compliance ─────────────────────────────────────────

export interface ComplianceRequirementData {
  id: string;
  framework: string;
  clause: string;
  title: string;
  description: string;
  applies_to: string;
}

export interface ComplianceEvidenceData {
  id: string;
  requirement_id: string;
  evidence_type: string;
  description: string;
  verified_by: string | null;
  verified_at: string | null;
}

export interface ComplianceStatusData {
  total_requirements: number;
  evidenced_requirements: number;
  verified_requirements: number;
  compliance_percentage: number;
}

export const compliance = {
  listRequirements: (token: string, framework?: string) => {
    const params = framework ? `?framework=${encodeURIComponent(framework)}` : "";
    return request<ComplianceRequirementData[]>(`/compliance/requirements${params}`, { token });
  },

  getStatus: (token: string) =>
    request<ComplianceStatusData>("/compliance/status", { token }),

  createEvidence: (
    data: { requirement_id: string; evidence_type: string; description: string },
    token: string
  ) =>
    request<ComplianceEvidenceData>("/compliance/evidence", {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),
};

// ── L12: Quality Management ──────────────────────────────────────

export interface QualityMetricData {
  id: string;
  name: string;
  description: string;
  target_value: number;
  unit: string;
}

export interface QualityDashboardMetricData {
  metric_id: string;
  name: string;
  target_value: number;
  latest_value: number | null;
  unit: string;
}

export interface QualityDashboardData {
  metrics: QualityDashboardMetricData[];
  total_feedback_count: number;
  average_rating: number | null;
}

export interface UserFeedbackData {
  id: string;
  user_id: string;
  category: string;
  text: string;
  rating: number;
}

export const quality = {
  listMetrics: (token: string) =>
    request<QualityMetricData[]>("/quality/metrics", { token }),

  getDashboard: (token: string) =>
    request<QualityDashboardData>("/quality/dashboard", { token }),

  createFeedback: (
    data: { category: string; text: string; rating: number },
    token: string
  ) =>
    request<UserFeedbackData>("/quality/feedback", {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),
};

// ── L08: Product Frontend / Preferences ──────────────────────────

export interface UserPreferenceData {
  id: string;
  user_id: string;
  theme: string;
  high_contrast: boolean;
  reduced_motion: boolean;
  font_size: number;
  locale: string;
}

export const preferences = {
  get: (token: string) =>
    request<UserPreferenceData>("/frontend-config/preferences", { token }),

  update: (
    data: {
      theme?: string;
      high_contrast?: boolean;
      reduced_motion?: boolean;
      font_size?: number;
      locale?: string;
    },
    token: string
  ) =>
    request<UserPreferenceData>("/frontend-config/preferences", {
      method: "PUT",
      body: JSON.stringify(data),
      token,
    }),
};

// ── L09: Dimensional Realization ─────────────────────────────────

export interface StageGateCriteriaData {
  id: string;
  stage: string;
  criteria: Record<string, unknown>;
  required_artifacts: unknown[];
}

export interface ProjectRealizationData {
  id: string;
  project_id: string;
  stage: string;
  evidence: string;
  approved_by: string | null;
}

export const realization = {
  listCriteria: (token: string) =>
    request<StageGateCriteriaData[]>("/realization/criteria", { token }),

  getCriteria: (stage: string, token: string) =>
    request<StageGateCriteriaData>(`/realization/criteria/${stage}`, { token }),

  advanceStage: (
    data: { project_id: string; target_stage: string; evidence?: string },
    token: string
  ) =>
    request<ProjectRealizationData>("/realization/advance", {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),
};

// ── L10: I/O Definition ──────────────────────────────────────────

export type IOType = "voice" | "touch" | "text" | "visual";

export interface IOCapabilityData {
  id: string;
  name: string;
  type: IOType;
  enabled: boolean;
}

export interface UserIOPreferenceData {
  id: string;
  user_id: string;
  input_mode: IOType;
  output_mode: IOType;
}

export const io = {
  listCapabilities: (token: string) =>
    request<IOCapabilityData[]>("/io/capabilities", { token }),

  getPreferences: (token: string) =>
    request<UserIOPreferenceData>("/io/preferences", { token }),

  updatePreferences: (
    data: { input_mode?: IOType; output_mode?: IOType },
    token: string
  ) =>
    request<UserIOPreferenceData>("/io/preferences", {
      method: "PUT",
      body: JSON.stringify(data),
      token,
    }),
};

// ── L13: Social & Engineering Impact ─────────────────────────────

export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface ImpactAssessmentData {
  id: string;
  title: string;
  category: string;
  description: string;
  risk_level: RiskLevel;
  mitigation: string;
}

export interface SurveyData {
  id: string;
  title: string;
  questions: unknown[];
}

export interface SurveyResponseData {
  id: string;
  survey_id: string;
  user_id: string;
  responses: Record<string, unknown>;
}

export const impact = {
  listAssessments: (token: string) =>
    request<ImpactAssessmentData[]>("/impact/assessments", { token }),

  listSurveys: (token: string) =>
    request<SurveyData[]>("/impact/surveys", { token }),

  submitSurveyResponse: (
    data: { survey_id: string; responses: Record<string, unknown> },
    token: string
  ) =>
    request<SurveyResponseData>("/impact/surveys/respond", {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),
};

