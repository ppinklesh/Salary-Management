"use client";

import { useCallback, useEffect, useState } from "react";
import { api, Employee, PaginatedResponse } from "@/lib/api";
import { EmployeeTable } from "./employee-table";
import { EmployeeFormDialog } from "./employee-form-dialog";
import { DeleteDialog } from "./delete-dialog";
import { EmployeeFilters } from "./employee-filters";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";

export function EmployeesClient() {
  const [data, setData] = useState<PaginatedResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [search, setSearch] = useState("");
  const [country, setCountry] = useState("");
  const [department, setDepartment] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [sortBy, setSortBy] = useState("id");
  const [sortOrder, setSortOrder] = useState("asc");

  const [formOpen, setFormOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
  const [deleteEmployee, setDeleteEmployee] = useState<Employee | null>(null);

  const fetchEmployees = useCallback(async () => {
    setLoading(true);
    try {
      const result = await api.employees.list({
        page,
        page_size: pageSize,
        search,
        country,
        department,
        job_title: jobTitle,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setData(result);
    } catch {
      toast.error("Failed to load employees");
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search, country, department, jobTitle, sortBy, sortOrder]);

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  const handleCreate = () => {
    setEditingEmployee(null);
    setFormOpen(true);
  };

  const handleEdit = (employee: Employee) => {
    setEditingEmployee(employee);
    setFormOpen(true);
  };

  const handleFormSuccess = () => {
    setFormOpen(false);
    setEditingEmployee(null);
    fetchEmployees();
  };

  const handleDeleteConfirm = async () => {
    if (!deleteEmployee) return;
    try {
      await api.employees.delete(deleteEmployee.id);
      toast.success(`${deleteEmployee.full_name} has been deleted`);
      setDeleteEmployee(null);
      fetchEmployees();
    } catch {
      toast.error("Failed to delete employee");
    }
  };

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(column);
      setSortOrder("asc");
    }
    setPage(1);
  };

  const handleSearch = (value: string) => {
    setSearch(value);
    setPage(1);
  };

  const handleFilterChange = (
    type: "country" | "department" | "jobTitle",
    value: string
  ) => {
    if (type === "country") setCountry(value);
    if (type === "department") setDepartment(value);
    if (type === "jobTitle") setJobTitle(value);
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Employees</h1>
          <p className="text-muted-foreground">
            Manage employee records and salary data
          </p>
        </div>
        <Button onClick={handleCreate}>
          <Plus className="h-4 w-4 mr-2" />
          Add Employee
        </Button>
      </div>

      <EmployeeFilters
        search={search}
        country={country}
        department={department}
        jobTitle={jobTitle}
        onSearch={handleSearch}
        onFilterChange={handleFilterChange}
      />

      {loading && !data ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full rounded" />
          ))}
        </div>
      ) : data ? (
        <EmployeeTable
          data={data}
          sortBy={sortBy}
          sortOrder={sortOrder}
          onSort={handleSort}
          onEdit={handleEdit}
          onDelete={setDeleteEmployee}
          onPageChange={setPage}
        />
      ) : null}

      <EmployeeFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        employee={editingEmployee}
        onSuccess={handleFormSuccess}
      />

      <DeleteDialog
        open={!!deleteEmployee}
        onOpenChange={(open) => !open && setDeleteEmployee(null)}
        employeeName={deleteEmployee?.full_name || ""}
        onConfirm={handleDeleteConfirm}
      />
    </div>
  );
}
