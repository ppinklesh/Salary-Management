"use client";

import { Employee, PaginatedResponse } from "@/lib/api";
import { Button, buttonVariants } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  MoreHorizontal,
  Pencil,
  UserMinus,
  UserPlus,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

import { convertLocalAmountToUsd, formatCurrencyCode, formatUsd } from "@/lib/currency";

function formatEmploymentType(type: string): string {
  return type.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatExitReason(reason: string): string {
  return reason.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function getEmploymentTypeVariant(
  employmentType: string
): "default" | "outline" | "secondary" {
  if (employmentType === "full_time") return "default";
  if (employmentType === "contractor") return "outline";
  return "secondary";
}

type Props = Readonly<{
  data: PaginatedResponse;
  sortBy: string;
  sortOrder: string;
  onSort: (column: string) => void;
  onEdit: (employee: Employee) => void;
  onOffboard: (employee: Employee) => void;
  onRehire: (employee: Employee) => void;
  onPageChange: (page: number) => void;
}>;

type SortIconProps = Readonly<{
  column: string;
  sortBy: string;
  sortOrder: string;
}>;

function SortIcon({ column, sortBy, sortOrder }: SortIconProps) {
  if (sortBy !== column) return <ArrowUpDown className="ml-1 h-3 w-3" />;
  return sortOrder === "asc" ? (
    <ArrowUp className="ml-1 h-3 w-3" />
  ) : (
    <ArrowDown className="ml-1 h-3 w-3" />
  );
}

type EmployeeRowActionsProps = Readonly<{
  employee: Employee;
  onEdit: (employee: Employee) => void;
  onOffboard: (employee: Employee) => void;
  onRehire: (employee: Employee) => void;
}>;

function EmployeeRowActions({
  employee,
  onEdit,
  onOffboard,
  onRehire,
}: EmployeeRowActionsProps) {
  if (employee.is_active) {
    return (
      <>
        <DropdownMenuItem onClick={() => onEdit(employee)}>
          <Pencil className="h-4 w-4 mr-2" />
          Edit
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => onOffboard(employee)}
          className="text-destructive focus:text-destructive"
        >
          <UserMinus className="h-4 w-4 mr-2" />
          Offboard
        </DropdownMenuItem>
      </>
    );
  }

  if (employee.exit_reason === "resigned") {
    return (
      <DropdownMenuItem onClick={() => onRehire(employee)}>
        <UserPlus className="h-4 w-4 mr-2" />
        Rehire
      </DropdownMenuItem>
    );
  }

  return null;
}

export function EmployeeTable({
  data,
  sortBy,
  sortOrder,
  onSort,
  onEdit,
  onOffboard,
  onRehire,
  onPageChange,
}: Props) {
  const columns = [
    { key: "full_name", label: "Name" },
    { key: "email", label: "Email" },
    { key: "job_title", label: "Job Title" },
    { key: "department", label: "Department" },
    { key: "country", label: "Country" },
    { key: "salary", label: "Salary" },
  ];

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((col) => (
                <TableHead key={col.key}>
                  <button
                    onClick={() => onSort(col.key)}
                    className="flex items-center font-medium hover:text-foreground transition-colors"
                  >
                    {col.label}
                    <SortIcon column={col.key} sortBy={sortBy} sortOrder={sortOrder} />
                  </button>
                </TableHead>
              ))}
              <TableHead className="w-24">Status</TableHead>
              <TableHead className="w-12">Type</TableHead>
              <TableHead className="w-10" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                  No employees found
                </TableCell>
              </TableRow>
            ) : (
              data.data.map((emp) => (
                <TableRow key={emp.id}>
                  <TableCell className="font-medium">{emp.full_name}</TableCell>
                  <TableCell className="text-muted-foreground">{emp.email}</TableCell>
                  <TableCell>{emp.job_title}</TableCell>
                  <TableCell>{emp.department}</TableCell>
                  <TableCell>{emp.country}</TableCell>
                  <TableCell>
                    <div className="font-mono">
                      {formatCurrencyCode(emp.salary, emp.currency)}
                    </div>
                    {emp.currency !== "USD" && (
                      <div className="text-xs text-muted-foreground font-mono">
                        ≈ {formatUsd(convertLocalAmountToUsd(emp.salary, emp.currency))} USD
                      </div>
                    )}
                  </TableCell>
                  <TableCell>
                    {emp.is_active ? (
                      <Badge variant="success">Active</Badge>
                    ) : (
                      <div className="space-y-1">
                        <Badge variant="warning">Inactive</Badge>
                        {emp.exit_reason && (
                          <p className="text-xs text-muted-foreground">
                            {formatExitReason(emp.exit_reason)}
                          </p>
                        )}
                      </div>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant={getEmploymentTypeVariant(emp.employment_type)}>
                      {formatEmploymentType(emp.employment_type)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger
                        className={cn(
                          buttonVariants({ variant: "ghost", size: "icon" }),
                          "h-8 w-8"
                        )}
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <EmployeeRowActions
                          employee={emp}
                          onEdit={onEdit}
                          onOffboard={onOffboard}
                          onRehire={onRehire}
                        />
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {(data.page - 1) * data.page_size + 1}–
          {Math.min(data.page * data.page_size, data.total)} of{" "}
          {data.total.toLocaleString()} employees
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(data.page - 1)}
            disabled={data.page <= 1}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>
          <span className="text-sm text-muted-foreground px-2">
            Page {data.page} of {data.total_pages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(data.page + 1)}
            disabled={data.page >= data.total_pages}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
