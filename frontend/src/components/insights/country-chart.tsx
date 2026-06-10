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
import { CountryStats } from "@/lib/api";
import { chartBarColor } from "@/lib/chart-colors";
import { convertLocalAmountToUsd, formatUsd, getLocalCurrency } from "@/lib/currency";

function formatAxisUsd(value: number): string {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return formatUsd(value);
}

interface Props {
  data: CountryStats[];
}

export function CountryChart({ data }: Props) {
  const chartData = data
    .sort((a, b) => b.avg_salary - a.avg_salary)
    .slice(0, 10)
    .map((item) => {
      const currency = getLocalCurrency(item.country);
      const avgUsd = convertLocalAmountToUsd(item.avg_salary, currency);
      return {
        name: item.country.length > 12 ? item.country.slice(0, 12) + "…" : item.country,
        avg_salary: Math.round(avgUsd),
        fullName: item.country,
        localAvg: item.avg_salary,
        currency,
      };
    });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Average Salary by Country</CardTitle>
        <p className="text-xs text-muted-foreground">
          Bars compare countries using USD equivalents (local amounts converted for display).
        </p>
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
            <YAxis tickFormatter={formatAxisUsd} tick={{ fontSize: 11 }} />
            <Tooltip
              formatter={(value) => [formatUsd(Number(value)), "Avg (USD equiv.)"]}
              labelFormatter={(_, payload) => {
                const row = payload?.[0]?.payload;
                if (!row) return "";
                return `${row.fullName} — local avg stored in DB`;
              }}
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
