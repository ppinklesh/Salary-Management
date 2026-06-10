"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, TrendingUp, TrendingDown, DollarSign } from "lucide-react";
import { SalarySummary } from "@/lib/api";
import { formatUsd } from "@/lib/currency";

function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

interface Props {
  summary: SalarySummary;
  countriesCount: number;
}

export function SummaryCards({ summary, countriesCount }: Props) {
  const cards = [
    {
      title: "Total Employees",
      value: formatNumber(summary.total_employees),
      icon: Users,
      description: `Across ${countriesCount} countries`,
      iconClass: "bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300",
    },
    {
      title: "Average Salary",
      value: formatUsd(summary.avg_salary),
      icon: DollarSign,
      description: `Median: ${formatUsd(summary.median_salary)}`,
      iconClass: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
    },
    {
      title: "Highest Salary",
      value: formatUsd(summary.max_salary),
      icon: TrendingUp,
      description: "Maximum across all employees",
      iconClass: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
    },
    {
      title: "Lowest Salary",
      value: formatUsd(summary.min_salary),
      icon: TrendingDown,
      description: "Minimum across all employees",
      iconClass: "bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300",
    },
  ];

  return (
    <div className="space-y-2">
      <p className="text-xs text-muted-foreground">Global salary figures normalized to USD for comparison.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.title}
              </CardTitle>
              <div className={`rounded-lg p-2 ${card.iconClass}`}>
                <card.icon className="h-4 w-4" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{card.value}</div>
              <p className="text-xs text-muted-foreground mt-1">{card.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
