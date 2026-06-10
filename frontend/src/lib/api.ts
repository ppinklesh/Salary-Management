const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const EXIT_REASONS = [
  "terminated",
  "resigned",
  "retired",
  "layoff",
  "end_of_contract",
  "other",
] as const;

export type ExitReason = (typeof EXIT_REASONS)[number];

export interface Employee {
  id: number;
  full_name: string;
  email: string;
  job_title: string;
  department: string;
  country: string;
  salary: number;
  currency: string;
  employment_type: string;
  hire_date: string;
  exit_date: string | null;
  exit_reason: ExitReason | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface PaginatedResponse {
  data: Employee[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface EmployeeOffboardData {
  exit_date: string;
  exit_reason: ExitReason;
}

export interface EmployeeFormData {
  full_name: string;
  email: string;
  job_title: string;
  department: string;
  country: string;
  salary: number;
  currency: string;
  employment_type: string;
  hire_date: string;
}

export interface SalarySummary {
  min_salary: number;
  max_salary: number;
  avg_salary: number;
  median_salary: number;
  total_employees: number;
}

export interface CountryStats {
  country: string;
  min_salary: number;
  max_salary: number;
  avg_salary: number;
  employee_count: number;
}

export interface JobTitleStats {
  job_title: string;
  avg_salary: number;
  min_salary: number;
  max_salary: number;
  employee_count: number;
}

export interface DepartmentStats {
  department: string;
  min_salary: number;
  max_salary: number;
  avg_salary: number;
  employee_count: number;
}

export const api = {
  employees: {
    list: (params: Record<string, string | number>) => {
      const query = new URLSearchParams();
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== "") query.set(k, String(v));
      });
      return fetchApi<PaginatedResponse>(`/api/v1/employees?${query}`);
    },
    get: (id: number) => fetchApi<Employee>(`/api/v1/employees/${id}`),
    create: (data: EmployeeFormData) =>
      fetchApi<Employee>("/api/v1/employees", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (id: number, data: Partial<EmployeeFormData>) =>
      fetchApi<Employee>(`/api/v1/employees/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    offboard: (id: number, data: EmployeeOffboardData) =>
      fetchApi<Employee>(`/api/v1/employees/${id}/offboard`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    rehire: (id: number) =>
      fetchApi<Employee>(`/api/v1/employees/${id}/rehire`, {
        method: "POST",
      }),
  },

  insights: {
    summary: () => fetchApi<SalarySummary>("/api/v1/insights/summary"),
    byCountry: () => fetchApi<CountryStats[]>("/api/v1/insights/by-country"),
    byJobTitle: (country?: string) => {
      const query = country ? `?country=${encodeURIComponent(country)}` : "";
      return fetchApi<JobTitleStats[]>(`/api/v1/insights/by-job-title${query}`);
    },
    byDepartment: () =>
      fetchApi<DepartmentStats[]>("/api/v1/insights/by-department"),
  },

  filters: {
    countries: () => fetchApi<string[]>("/api/v1/filters/countries"),
    departments: () => fetchApi<string[]>("/api/v1/filters/departments"),
    jobTitles: () => fetchApi<string[]>("/api/v1/filters/job-titles"),
  },
};
