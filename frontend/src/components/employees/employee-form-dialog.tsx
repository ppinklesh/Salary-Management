"use client";

import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { api, Employee, EmployeeFormData } from "@/lib/api";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

const COUNTRIES_CURRENCIES = [
  { country: "United States", currency: "USD" },
  { country: "United Kingdom", currency: "GBP" },
  { country: "Germany", currency: "EUR" },
  { country: "France", currency: "EUR" },
  { country: "India", currency: "INR" },
  { country: "Canada", currency: "CAD" },
  { country: "Australia", currency: "AUD" },
  { country: "Japan", currency: "JPY" },
  { country: "Brazil", currency: "BRL" },
  { country: "Singapore", currency: "SGD" },
  { country: "Netherlands", currency: "EUR" },
  { country: "Sweden", currency: "SEK" },
];

const DEPARTMENTS = [
  "Engineering", "Product", "Marketing", "Sales", "Human Resources",
  "Finance", "Operations", "Design", "Legal", "Customer Support",
];

const JOB_TITLES = [
  "Software Engineer", "Senior Software Engineer", "Staff Engineer",
  "Engineering Manager", "Product Manager", "Senior Product Manager",
  "Data Analyst", "Data Scientist", "Marketing Specialist",
  "Sales Representative", "Account Executive", "HR Specialist",
  "Financial Analyst", "Operations Manager", "UX Designer",
  "UI Designer", "Legal Counsel", "Support Specialist",
  "DevOps Engineer", "QA Engineer",
];

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  employee: Employee | null;
  onSuccess: () => void;
}

const defaultForm: EmployeeFormData = {
  full_name: "",
  email: "",
  job_title: "",
  department: "",
  country: "",
  salary: 0,
  currency: "USD",
  employment_type: "full_time",
  hire_date: new Date().toISOString().split("T")[0],
};

export function EmployeeFormDialog({ open, onOpenChange, employee, onSuccess }: Props) {
  const [form, setForm] = useState<EmployeeFormData>(defaultForm);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const isEdit = !!employee;

  useEffect(() => {
    if (employee) {
      setForm({
        full_name: employee.full_name,
        email: employee.email,
        job_title: employee.job_title,
        department: employee.department,
        country: employee.country,
        salary: employee.salary,
        currency: employee.currency,
        employment_type: employee.employment_type,
        hire_date: employee.hire_date,
      });
    } else {
      setForm(defaultForm);
    }
    setErrors({});
  }, [employee, open]);

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.full_name.trim()) errs.full_name = "Name is required";
    if (!form.email.trim()) errs.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(form.email)) errs.email = "Invalid email";
    if (!form.job_title) errs.job_title = "Job title is required";
    if (!form.department) errs.department = "Department is required";
    if (!form.country) errs.country = "Country is required";
    if (!form.salary || form.salary <= 0) errs.salary = "Salary must be positive";
    if (!form.hire_date) errs.hire_date = "Hire date is required";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setSaving(true);
    try {
      if (isEdit && employee) {
        await api.employees.update(employee.id, form);
        toast.success(`${form.full_name} updated successfully`);
      } else {
        await api.employees.create(form);
        toast.success(`${form.full_name} added successfully`);
      }
      onSuccess();
    } catch (err: any) {
      toast.error(err.message || "Failed to save employee");
    } finally {
      setSaving(false);
    }
  };

  const handleCountryChange = (value: string | null) => {
    if (!value) return;
    const match = COUNTRIES_CURRENCIES.find((c) => c.country === value);
    setForm((prev) => ({
      ...prev,
      country: value,
      currency: match?.currency || prev.currency,
    }));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit Employee" : "Add Employee"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <Label htmlFor="full_name">Full Name</Label>
              <Input
                id="full_name"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                placeholder="John Doe"
              />
              {errors.full_name && <p className="text-sm text-destructive mt-1">{errors.full_name}</p>}
            </div>

            <div className="col-span-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="john.doe@acme.com"
              />
              {errors.email && <p className="text-sm text-destructive mt-1">{errors.email}</p>}
            </div>

            <div>
              <Label>Country</Label>
              <Select value={form.country} onValueChange={handleCountryChange}>
                <SelectTrigger>
                  <SelectValue placeholder="Select country" />
                </SelectTrigger>
                <SelectContent>
                  {COUNTRIES_CURRENCIES.map((c) => (
                    <SelectItem key={c.country} value={c.country}>
                      {c.country}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.country && <p className="text-sm text-destructive mt-1">{errors.country}</p>}
            </div>

            <div>
              <Label>Department</Label>
              <Select value={form.department} onValueChange={(v) => v && setForm({ ...form, department: v })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  {DEPARTMENTS.map((d) => (
                    <SelectItem key={d} value={d}>
                      {d}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.department && <p className="text-sm text-destructive mt-1">{errors.department}</p>}
            </div>

            <div className="col-span-2">
              <Label>Job Title</Label>
              <Select value={form.job_title} onValueChange={(v) => v && setForm({ ...form, job_title: v })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select job title" />
                </SelectTrigger>
                <SelectContent>
                  {JOB_TITLES.map((j) => (
                    <SelectItem key={j} value={j}>
                      {j}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.job_title && <p className="text-sm text-destructive mt-1">{errors.job_title}</p>}
            </div>

            <div>
              <Label htmlFor="salary">Salary</Label>
              <Input
                id="salary"
                type="number"
                value={form.salary || ""}
                onChange={(e) => setForm({ ...form, salary: parseFloat(e.target.value) || 0 })}
                placeholder="95000"
                min="0"
                step="1000"
              />
              {errors.salary && <p className="text-sm text-destructive mt-1">{errors.salary}</p>}
            </div>

            <div>
              <Label>Employment Type</Label>
              <Select value={form.employment_type} onValueChange={(v) => v && setForm({ ...form, employment_type: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="full_time">Full Time</SelectItem>
                  <SelectItem value="part_time">Part Time</SelectItem>
                  <SelectItem value="contract">Contract</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="hire_date">Hire Date</Label>
              <Input
                id="hire_date"
                type="date"
                value={form.hire_date}
                onChange={(e) => setForm({ ...form, hire_date: e.target.value })}
              />
              {errors.hire_date && <p className="text-sm text-destructive mt-1">{errors.hire_date}</p>}
            </div>

            <div>
              <Label>Currency</Label>
              <Input value={form.currency} disabled className="bg-muted" />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              {isEdit ? "Update" : "Add"} Employee
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
