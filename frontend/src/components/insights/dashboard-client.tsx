"use client";

import { useEffect, useState } from "react";
import { api, SalarySummary, CountryStats, DepartmentStats, JobTitleStats } from "@/lib/api";
import { SummaryCards } from "./summary-cards";
import { CountryChart } from "./country-chart";
import { CountryTable } from "./country-table";
import { DepartmentChart } from "./department-chart";
import { JobTitleChart } from "./job-title-chart";
import { Skeleton } from "@/components/ui/skeleton";

export function DashboardClient() {
  const [summary, setSummary] = useState<SalarySummary | null>(null);
  const [countryStats, setCountryStats] = useState<CountryStats[]>([]);
  const [deptStats, setDeptStats] = useState<DepartmentStats[]>([]);
  const [jobTitleStats, setJobTitleStats] = useState<JobTitleStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [s, c, d, j] = await Promise.all([
          api.insights.summary(),
          api.insights.byCountry(),
          api.insights.byDepartment(),
          api.insights.byJobTitle(),
        ]);
        setSummary(s);
        setCountryStats(c);
        setDeptStats(d);
        setJobTitleStats(j);
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Salary Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-xl" />
          ))}
        </div>
        <Skeleton className="h-80 rounded-xl" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Salary Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of compensation across the organization
        </p>
      </div>

      {summary && <SummaryCards summary={summary} countriesCount={countryStats.length} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CountryChart data={countryStats} />
        <DepartmentChart data={deptStats} />
      </div>

      <JobTitleChart data={jobTitleStats} />

      <CountryTable data={countryStats} />
    </div>
  );
}
