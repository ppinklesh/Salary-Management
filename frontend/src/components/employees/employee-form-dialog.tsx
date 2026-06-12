"use client";

import { useEffect, useState, type SubmitEvent } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { api, Employee, EmployeeFormData } from "@/lib/api";
import {
  COUNTRY_CURRENCY,
  convertLocalToUsd,
  formatUsd,
  getLocalCurrency,
} from "@/lib/currency";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { Briefcase, Loader2, MapPin, User, type LucideIcon } from "lucide-react";

const COUNTRIES = Object.keys(COUNTRY_CURRENCY);

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
  readonly open: boolean;
  readonly onOpenChange: (open: boolean) => void;
  readonly employee: Employee | null;
  readonly onSuccess: () => void;
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

interface FormSectionProps {
  readonly icon: LucideIcon;
  readonly title: string;
  readonly description: string;
  readonly children: React.ReactNode;
}

function FormSection({
  icon: Icon,
  title,
  description,
  children,
}: FormSectionProps) {
  return (
    <section className="space-y-4">
      <div className="flex items-start gap-3">
        <div className="rounded-lg bg-primary/10 p-2 text-primary">
          <Icon className="h-4 w-4" />
        </div>
        <div>
          <h3 className="text-sm font-medium">{title}</h3>
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">{children}</div>
    </section>
  );
}

interface FormFieldProps {
  readonly label: string;
  readonly htmlFor?: string;
  readonly error?: string;
  readonly className?: string;
  readonly children: React.ReactNode;
}

function FormField({
  label,
  htmlFor,
  error,
  className,
  children,
}: FormFieldProps) {
  return (
    <div className={cn("space-y-1.5", className)}>
      <Label htmlFor={htmlFor}>{label}</Label>
      {children}
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}

export function EmployeeFormDialog({ open, onOpenChange, employee, onSuccess }: Props) {
  const [form, setForm] = useState<EmployeeFormData>(defaultForm);
  const [localSalary, setLocalSalary] = useState(0);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const isEdit = !!employee;
  const localCurrency = form.country ? getLocalCurrency(form.country) : null;
  const usdEquivalent =
    form.country && localSalary > 0
      ? Math.round(convertLocalToUsd(localSalary, form.country) * 100) / 100
      : 0;
  const showUsdPreview = Boolean(form.country && localSalary > 0);

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
      setLocalSalary(employee.salary);
    } else {
      setForm(defaultForm);
      setLocalSalary(0);
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
    if (!localSalary || localSalary <= 0) errs.salary = "Salary must be positive";
    if (!form.hire_date) errs.hire_date = "Hire date is required";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!validate()) return;

    setSaving(true);
    const payload = {
      ...form,
      salary: localSalary,
      currency: getLocalCurrency(form.country),
    };
    try {
      if (isEdit && employee) {
        await api.employees.update(employee.id, payload);
        toast.success(`${form.full_name} updated successfully`);
      } else {
        await api.employees.create(payload);
        toast.success(`${form.full_name} added successfully`);
      }
      onSuccess();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to save employee";
      toast.error(message);
    } finally {
      setSaving(false);
    }
  };

  const handleCountryChange = (value: string | null) => {
    if (!value) return;
    setForm((prev) => ({ ...prev, country: value }));
  };

  const salaryLabel = localCurrency
    ? `Annual salary (${localCurrency})`
    : "Annual salary (local currency)";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit Employee" : "Add Employee"}</DialogTitle>
          <DialogDescription>
            {isEdit
              ? "Update profile, role, and compensation details for this employee."
              : "Create a new employee record with role and salary information."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <FormSection
            icon={User}
            title="Personal details"
            description="Basic contact information for the employee."
          >
            <FormField label="Full name" htmlFor="full_name" error={errors.full_name} className="sm:col-span-2">
              <Input
                id="full_name"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                placeholder="John Doe"
              />
            </FormField>

            <FormField label="Email" htmlFor="email" error={errors.email} className="sm:col-span-2">
              <Input
                id="email"
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="john.doe@acme.com"
              />
            </FormField>

            <FormField label="Hire date" htmlFor="hire_date" error={errors.hire_date}>
              <Input
                id="hire_date"
                type="date"
                value={form.hire_date}
                onChange={(e) => setForm({ ...form, hire_date: e.target.value })}
              />
            </FormField>

            <FormField label="Employment type">
              <Select value={form.employment_type} onValueChange={(v) => v && setForm({ ...form, employment_type: v })}>
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="full_time">Full Time</SelectItem>
                  <SelectItem value="part_time">Part Time</SelectItem>
                  <SelectItem value="contract">Contract</SelectItem>
                </SelectContent>
              </Select>
            </FormField>
          </FormSection>

          <Separator />

          <FormSection
            icon={Briefcase}
            title="Role & department"
            description="Where they work and what they do."
          >
            <FormField label="Department" error={errors.department}>
              <Select value={form.department} onValueChange={(v) => v && setForm({ ...form, department: v })}>
                <SelectTrigger className="w-full">
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
            </FormField>

            <FormField label="Job title" error={errors.job_title}>
              <Select value={form.job_title} onValueChange={(v) => v && setForm({ ...form, job_title: v })}>
                <SelectTrigger className="w-full">
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
            </FormField>
          </FormSection>

          <Separator />

          <FormSection
            icon={MapPin}
            title="Location & compensation"
            description="Enter salary in the employee's local currency. The exact amount is stored — USD is shown only as a reference."
          >
            <FormField label="Country" error={errors.country}>
              <Select value={form.country} onValueChange={handleCountryChange}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select country" />
                </SelectTrigger>
                <SelectContent>
                  {COUNTRIES.map((country) => (
                    <SelectItem key={country} value={country}>
                      {country} ({getLocalCurrency(country)})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormField>

            <FormField
              label={salaryLabel}
              htmlFor="local_salary"
              error={errors.salary}
              className="sm:col-span-2"
            >
              <div className="relative">
                <span className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
                  {localCurrency ?? "—"}
                </span>
                <Input
                  id="local_salary"
                  type="number"
                  value={localSalary || ""}
                  onChange={(e) => setLocalSalary(Number.parseFloat(e.target.value) || 0)}
                  placeholder={localCurrency === "INR" ? "1500000" : "95000"}
                  min="0"
                  step={localCurrency === "JPY" ? "10000" : "1000"}
                  disabled={!form.country}
                  className={cn("pl-14", !form.country && "bg-muted")}
                />
              </div>
              {!form.country && (
                <p className="text-xs text-muted-foreground">Select a country first to enter salary.</p>
              )}
              {showUsdPreview && (
                <p className="text-xs text-muted-foreground">
                  USD value will be{" "}
                  <span className="font-medium text-foreground">{formatUsd(usdEquivalent)}</span>
                  {localCurrency !== "USD" && " (approx. exchange rate)"}
                </p>
              )}
            </FormField>
          </FormSection>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              {isEdit ? "Save changes" : "Add employee"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
