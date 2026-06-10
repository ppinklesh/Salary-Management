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
import { formatCurrencyCode, getLocalCurrency } from "@/lib/currency";

interface Props {
  data: CountryStats[];
}

export function CountryTable({ data }: Props) {
  const sorted = [...data].sort((a, b) => b.employee_count - a.employee_count);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Salary Breakdown by Country</CardTitle>
        <p className="text-xs text-muted-foreground">
          Amounts stored and shown in each country&apos;s local currency.
        </p>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Country</TableHead>
              <TableHead className="text-right">Employees</TableHead>
              <TableHead className="text-right">Min (local)</TableHead>
              <TableHead className="text-right">Max (local)</TableHead>
              <TableHead className="text-right">Avg (local)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sorted.map((row) => {
              const currency = getLocalCurrency(row.country);
              return (
                <TableRow key={row.country}>
                  <TableCell className="font-medium">{row.country}</TableCell>
                  <TableCell className="text-right">
                    {row.employee_count.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrencyCode(row.min_salary, currency)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrencyCode(row.max_salary, currency)}
                  </TableCell>
                  <TableCell className="text-right font-medium font-mono">
                    {formatCurrencyCode(row.avg_salary, currency)}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
