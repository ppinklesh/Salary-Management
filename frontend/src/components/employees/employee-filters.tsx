"use client";

import { useEffect, useRef, useState } from "react";
import { Input } from "@/components/ui/input";
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
  search: string;
  country: string;
  department: string;
  jobTitle: string;
  status: string;
  onSearch: (value: string) => void;
  onFilterChange: (
    type: "country" | "department" | "jobTitle" | "status",
    value: string
  ) => void;
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
    <div className="flex flex-wrap items-center gap-3">
      <div className="relative flex-1 min-w-[200px] max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search by name..."
          value={localSearch}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="pl-9"
        />
      </div>

      <Select value={status} onValueChange={(v) => v && onFilterChange("status", v)}>
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="Active" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="active">Active</SelectItem>
          <SelectItem value="inactive">Inactive</SelectItem>
          <SelectItem value="all">All</SelectItem>
        </SelectContent>
      </Select>

      <Select value={country || "all"} onValueChange={(v) => onFilterChange("country", !v || v === "all" ? "" : v)}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="All Countries" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Countries</SelectItem>
          {countries.map((c) => (
            <SelectItem key={c} value={c}>
              {c}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={department || "all"} onValueChange={(v) => onFilterChange("department", !v || v === "all" ? "" : v)}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="All Departments" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Departments</SelectItem>
          {departments.map((d) => (
            <SelectItem key={d} value={d}>
              {d}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={jobTitle || "all"} onValueChange={(v) => onFilterChange("jobTitle", !v || v === "all" ? "" : v)}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="All Job Titles" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Job Titles</SelectItem>
          {jobTitles.map((j) => (
            <SelectItem key={j} value={j}>
              {j}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {hasFilters && (
        <Button variant="ghost" size="sm" onClick={clearFilters}>
          <X className="h-4 w-4 mr-1" />
          Clear
        </Button>
      )}
    </div>
  );
}
