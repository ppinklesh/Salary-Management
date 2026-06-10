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
import { DepartmentStats } from "@/lib/api";
import { chartBarColor } from "@/lib/chart-colors";

function formatCurrency(value: number): string {
  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
  return `$${value}`;
}

interface Props {
  data: DepartmentStats[];
}

export function DepartmentChart({ data }: Props) {
  const chartData = data
    .sort((a, b) => b.avg_salary - a.avg_salary)
    .map((item) => ({
      name: item.department.length > 14 ? item.department.slice(0, 14) + "…" : item.department,
      avg_salary: Math.round(item.avg_salary),
      fullName: item.department,
      count: item.employee_count,
    }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Average Salary by Department</CardTitle>
        <p className="text-xs text-muted-foreground">USD equivalents for cross-department comparison.</p>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 11 }}
              angle={-30}
              textAnchor="end"
              height={60}
            />
            <YAxis tickFormatter={formatCurrency} tick={{ fontSize: 11 }} />
            <Tooltip
              formatter={(value) => [
                `$${Number(value).toLocaleString()}`,
                "Avg Salary",
              ]}
              labelFormatter={(_, payload) =>
                payload?.[0]?.payload?.fullName || ""
              }
            />
            <Bar dataKey="avg_salary" radius={[4, 4, 0, 0]}>
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
