import { Suspense } from "react";
import { EmployeesClient } from "@/components/employees/employees-client";
import { Skeleton } from "@/components/ui/skeleton";

export default function EmployeesPage() {
  return (
    <Suspense
      fallback={
        <div className="space-y-6">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      }
    >
      <EmployeesClient />
    </Suspense>
  );
}
