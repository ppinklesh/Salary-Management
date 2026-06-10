"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { JobTitleStats } from "@/lib/api";
import { chartBarColor } from "@/lib/chart-colors";

function formatCurrency(value: number): string {
  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
  return `$${value}`;
}

interface Props {
  data: JobTitleStats[];
}

export function JobTitleChart({ data }: Props) {
  const chartData = data
    .sort((a, b) => b.avg_salary - a.avg_salary)
    .slice(0, 12)
    .map((item) => ({
      name: item.job_title.length > 18 ? item.job_title.slice(0, 18) + "…" : item.job_title,
      avg_salary: Math.round(item.avg_salary),
      fullName: item.job_title,
      count: item.employee_count,
    }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Average Salary by Job Title (Top 12)</CardTitle>
        <p className="text-xs text-muted-foreground">USD equivalents for cross-role comparison.</p>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 0, right: 20, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis type="number" tickFormatter={formatCurrency} tick={{ fontSize: 11 }} />
            <YAxis
              dataKey="name"
              type="category"
              width={140}
              tick={{ fontSize: 11 }}
            />
            <Tooltip
              formatter={(value) => [
                `$${Number(value).toLocaleString()}`,
                "Avg Salary",
              ]}
              labelFormatter={(_, payload) =>
                `${payload?.[0]?.payload?.fullName} (${payload?.[0]?.payload?.count} employees)`
              }
            />
            <Bar dataKey="avg_salary" radius={[0, 4, 4, 0]}>
              {chartData.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={chartBarColor(index)}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
