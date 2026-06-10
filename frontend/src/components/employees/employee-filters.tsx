"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

interface Props {
  readonly search: string;
  readonly country: string;
  readonly department: string;
  readonly jobTitle: string;
  readonly status: string;
  readonly onSearch: (value: string) => void;
  readonly onFilterChange: (
    type: "country" | "department" | "jobTitle" | "status",
    value: string
  ) => void;
}

const controlClass = "h-8";

interface FilterFieldProps {
  readonly label: string;
  readonly htmlFor: string;
  readonly className?: string;
  readonly children: ReactNode;
}

function FilterField({
  label,
  htmlFor,
  className,
  children,
}: FilterFieldProps) {
  return (
    <div className={className}>
      <Label htmlFor={htmlFor} className="mb-1.5 block h-4 leading-4">
        {label}
      </Label>
      <div className={`${controlClass} flex items-center`}>{children}</div>
    </div>
  );
}

export function EmployeeFilters({
  search,
  country,
  department,
  jobTitle,
  status,
  onSearch,
  onFilterChange,
}: Props) {
  const [countries, setCountries] = useState<string[]>([]);
  const [departments, setDepartments] = useState<string[]>([]);
  const [jobTitles, setJobTitles] = useState<string[]>([]);
  const [localSearch, setLocalSearch] = useState(search);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    Promise.all([
      api.filters.countries(),
      api.filters.departments(),
      api.filters.jobTitles(),
    ]).then(([c, d, j]) => {
      setCountries(c);
      setDepartments(d);
      setJobTitles(j);
    });
  }, []);

  useEffect(() => {
    setLocalSearch(search);
  }, [search]);

  const handleSearchChange = (value: string) => {
    setLocalSearch(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => onSearch(value), 300);
  };

  const hasFilters = country || department || jobTitle || search || status !== "active";

  const clearFilters = () => {
    onSearch("");
    onFilterChange("country", "");
    onFilterChange("department", "");
    onFilterChange("jobTitle", "");
    onFilterChange("status", "active");
    setLocalSearch("");
  };

  return (
    <div className="flex flex-wrap items-end gap-3">
      <FilterField label="Search" htmlFor="employee-search" className="w-[220px]">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            id="employee-search"
            placeholder="Search by name..."
            value={localSearch}
            onChange={(e) => handleSearchChange(e.target.value)}
            className={`${controlClass} w-full pl-9`}
          />
        </div>
      </FilterField>

      <FilterField label="Status" htmlFor="employee-status" className="w-[160px]">
        <Select value={status} onValueChange={(v) => v && onFilterChange("status", v)}>
          <SelectTrigger id="employee-status" className={`${controlClass} w-full`}>
            <SelectValue placeholder="Active" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
            <SelectItem value="all">All</SelectItem>
          </SelectContent>
        </Select>
      </FilterField>

      <FilterField label="Country" htmlFor="employee-country" className="w-[180px]">
        <Select
          value={country || "all"}
          onValueChange={(v) => onFilterChange("country", !v || v === "all" ? "" : v)}
        >
          <SelectTrigger id="employee-country" className={`${controlClass} w-full`}>
            <SelectValue placeholder="All countries" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All countries</SelectItem>
            {countries.map((c) => (
              <SelectItem key={c} value={c}>
                {c}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </FilterField>

      <FilterField label="Department" htmlFor="employee-department" className="w-[180px]">
        <Select
          value={department || "all"}
          onValueChange={(v) => onFilterChange("department", !v || v === "all" ? "" : v)}
        >
          <SelectTrigger id="employee-department" className={`${controlClass} w-full`}>
            <SelectValue placeholder="All departments" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All departments</SelectItem>
            {departments.map((d) => (
              <SelectItem key={d} value={d}>
                {d}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </FilterField>

      <FilterField label="Job title" htmlFor="employee-job-title" className="w-[180px]">
        <Select
          value={jobTitle || "all"}
          onValueChange={(v) => onFilterChange("jobTitle", !v || v === "all" ? "" : v)}
        >
          <SelectTrigger id="employee-job-title" className={`${controlClass} w-full`}>
            <SelectValue placeholder="All job titles" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All job titles</SelectItem>
            {jobTitles.map((j) => (
              <SelectItem key={j} value={j}>
                {j}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </FilterField>

      {hasFilters && (
        <div>
          <span className="mb-1.5 block h-4" aria-hidden="true" />
          <div className={`${controlClass} flex items-center`}>
            <Button variant="ghost" size="sm" onClick={clearFilters} className="h-8 px-3">
              <X className="mr-1 h-4 w-4" />
              Clear
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
