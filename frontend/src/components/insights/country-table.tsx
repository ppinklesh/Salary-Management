"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { CountryStats } from "@/lib/api";

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

interface Props {
  data: CountryStats[];
}

export function CountryTable({ data }: Props) {
  const sorted = [...data].sort((a, b) => b.employee_count - a.employee_count);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Salary Breakdown by Country</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Country</TableHead>
              <TableHead className="text-right">Employees</TableHead>
              <TableHead className="text-right">Min Salary</TableHead>
              <TableHead className="text-right">Max Salary</TableHead>
              <TableHead className="text-right">Avg Salary</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sorted.map((row) => (
              <TableRow key={row.country}>
                <TableCell className="font-medium">{row.country}</TableCell>
                <TableCell className="text-right">
                  {row.employee_count.toLocaleString()}
                </TableCell>
                <TableCell className="text-right">
                  {formatCurrency(row.min_salary)}
                </TableCell>
                <TableCell className="text-right">
                  {formatCurrency(row.max_salary)}
                </TableCell>
                <TableCell className="text-right font-medium">
                  {formatCurrency(row.avg_salary)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
