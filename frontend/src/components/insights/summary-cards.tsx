"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, TrendingUp, TrendingDown, DollarSign, Globe } from "lucide-react";
import { SalarySummary } from "@/lib/api";

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

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
    },
    {
      title: "Average Salary",
      value: formatCurrency(summary.avg_salary),
      icon: DollarSign,
      description: `Median: ${formatCurrency(summary.median_salary)}`,
    },
    {
      title: "Highest Salary",
      value: formatCurrency(summary.max_salary),
      icon: TrendingUp,
      description: "Maximum across all employees",
    },
    {
      title: "Lowest Salary",
      value: formatCurrency(summary.min_salary),
      icon: TrendingDown,
      description: "Minimum across all employees",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {card.title}
            </CardTitle>
            <card.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {card.description}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
