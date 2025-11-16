import axios, { AxiosError } from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      const detail = (error.response.data as { detail?: string })?.detail
      throw new Error(detail || `Server error: ${error.response.status}`)
    } else if (error.request) {
      throw new Error('Network error: Unable to reach the server')
    } else {
      throw new Error('Request failed: ' + error.message)
    }
  }
)

export interface Script {
  id: number
  title: string
  predicted_rating: string | null
  agg_scores: Record<string, number> | null
  model_version: string | null
  total_scenes: number | null
  created_at: string
  updated_at: string | null
  reasons?: string[]
  evidence_excerpts?: string[]
}

export interface Scene {
  id: number
  scene_id: number
  heading: string
  violence: number
  gore: number
  sex_act: number
  nudity: number
  profanity: number
  drugs: number
  child_risk: number
  weight: number
  sample_text: string | null
  recommendations?: string[]
}

export interface ScriptDetail extends Script {
  content: string
  scenes: Scene[]
}

export interface RatingJob {
  job_id: string
  script_id: number
  status: string
  message: string
}

export interface WhatIfResponse {
  original_rating: string
  modified_rating: string
  original_scores: Record<string, number>
  modified_scores: Record<string, number>
  changes_applied: string[]
  explanation: string
  rating_changed: boolean
}

export interface ModificationConfig {
  type: string
  params: Record<string, any>
  targets?: {
    entity_type?: string
    entity_names?: string[]
  }
  scope?: number[]
}

export interface EntityInfo {
  type: string
  name: string
  mentions: number
  scenes: number[]
}

export interface SceneInfo {
  scene_id: number
  scene_type: string
  characters: string[]
  location: string | null
  summary: string | null
}

export interface AdvancedWhatIfResponse {
  original_rating: string
  modified_rating: string
  original_scores: Record<string, number>
  modified_scores: Record<string, number>
  modifications_applied: Array<{
    type: string
    metadata?: Record<string, any>
    error?: string
  }>
  entities_extracted: EntityInfo[]
  scene_analysis: SceneInfo[]
  explanation: string
  modified_script: string | null
  rating_changed: boolean
}

export interface SmartSuggestion {
  text: string
  category: string
  icon: string
  priority: number
  confidence: number
  affected_scenes: number[]
  reasoning: string
}

export interface SmartSuggestionsResponse {
  suggestions: SmartSuggestion[]
  analysis_summary: string
  current_rating: string
  total_scenes: number
}

export interface LineMatch {
  text: string
  start: number
  end: number
  pattern: string
}

export interface LineDetection {
  id?: number
  line_start: number
  line_end: number
  detected_text: string
  context_before: string | null
  context_after: string | null
  category: string
  severity: number
  parents_guide_severity?: string
  character_name?: string
  page_number?: number
  matched_patterns: {
    count: number
    matches: LineMatch[]
  }
  is_false_positive?: boolean
  user_corrected?: boolean
  created_at?: string
}

export interface ParentsGuideCategoryStats {
  severity: string
  episode_count: number
  percentage: number
  top_matches: number
}

export interface LineDetectionStats {
  total_detections: number
  by_category: Record<string, number>
  total_matches: Record<string, number>
  false_positives: number
  user_corrections: number
  parents_guide?: Record<string, ParentsGuideCategoryStats>
}

export interface ScriptWithDetections {
  script_id: number
  title: string
  predicted_rating: string | null
  detections: LineDetection[]
  stats: LineDetectionStats
  correction_count: number
}

export interface UserCorrection {
  id?: number
  script_id: number
  detection_id?: number
  correction_type: string
  line_start?: number
  line_end?: number
  category?: string
  severity?: number
  note?: string
  created_at?: string
}

export const scriptsApi = {
  list: async (): Promise<Script[]> => {
    const { data } = await apiClient.get('/scripts/')
    return data
  },

  get: async (id: number): Promise<ScriptDetail> => {
    const { data } = await apiClient.get(`/scripts/${id}`)
    return data
  },

  create: async (title: string, content: string): Promise<Script> => {
    const { data } = await apiClient.post('/scripts/', { title, content })
    return data
  },

  upload: async (file: File, title?: string): Promise<Script> => {
    const formData = new FormData()
    formData.append('file', file)
    if (title) formData.append('title', title)

    const { data } = await apiClient.post('/scripts/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  rate: async (id: number, background = true): Promise<RatingJob> => {
    const { data } = await apiClient.post(`/scripts/${id}/rate?background=${background}`)
    return data
  },

  jobStatus: async (jobId: string) => {
    const { data } = await apiClient.get(`/scripts/jobs/${jobId}/status`)
    return data
  },

  whatIf: async (id: number, modificationRequest: string): Promise<WhatIfResponse> => {
    const { data } = await apiClient.post(`/scripts/${id}/what-if`, {
      script_id: id,
      modification_request: modificationRequest
    })
    return data
  },

  whatIfAdvanced: async (
    scriptText: string,
    modifications: ModificationConfig[]
  ): Promise<AdvancedWhatIfResponse> => {
    const mlServiceUrl = import.meta.env.VITE_ML_SERVICE_URL || 'http://localhost:8001'
    const { data } = await axios.post(`${mlServiceUrl}/what_if_advanced`, {
      script_text: scriptText,
      modifications,
      use_llm: false,
      preserve_structure: true
    })
    return data
  },

  getSmartSuggestions: async (
    scriptText: string,
    currentScores?: Record<string, number>,
    currentRating?: string,
    language: string = 'ru',
    maxSuggestions: number = 8
  ): Promise<SmartSuggestionsResponse> => {
    const mlServiceUrl = import.meta.env.VITE_ML_SERVICE_URL || 'http://localhost:8001'
    const { data } = await axios.post(`${mlServiceUrl}/what_if_suggestions`, {
      script_text: scriptText,
      current_scores: currentScores,
      current_rating: currentRating,
      language,
      max_suggestions: maxSuggestions
    })
    return data
  },

  detectLines: async (scriptId: number, contextSize: number = 3): Promise<LineDetection[]> => {
    const { data } = await apiClient.post(`/scripts/${scriptId}/detections?context_size=${contextSize}`)
    return data
  },

  getDetections: async (scriptId: number, includeFalsePositives: boolean = false): Promise<LineDetection[]> => {
    const { data } = await apiClient.get(`/scripts/${scriptId}/detections?include_false_positives=${includeFalsePositives}`)
    return data
  },

  getDetectionStats: async (scriptId: number): Promise<LineDetectionStats> => {
    const { data } = await apiClient.get(`/scripts/${scriptId}/detections/stats`)
    return data
  },

  getScriptWithDetections: async (scriptId: number, includeFalsePositives: boolean = false): Promise<ScriptWithDetections> => {
    const { data } = await apiClient.get(`/scripts/${scriptId}/detections/full?include_false_positives=${includeFalsePositives}`)
    return data
  },

  markFalsePositive: async (detectionId: number, isFalsePositive: boolean): Promise<LineDetection> => {
    const { data } = await apiClient.patch(`/scripts/detections/${detectionId}/false-positive?is_false_positive=${isFalsePositive}`)
    return data
  },

  createCorrection: async (scriptId: number, correction: Omit<UserCorrection, 'id' | 'created_at'>): Promise<UserCorrection> => {
    const { data } = await apiClient.post(`/scripts/${scriptId}/corrections`, correction)
    return data
  },

  getCorrections: async (scriptId: number): Promise<UserCorrection[]> => {
    const { data } = await apiClient.get(`/scripts/${scriptId}/corrections`)
    return data
  },
}

export default apiClient
