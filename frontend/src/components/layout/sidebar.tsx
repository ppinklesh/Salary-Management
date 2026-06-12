"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Users, Building2, UserPlus } from "lucide-react";
import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";

const navItems = [
  { href: "/", label: "Dashboard", icon: BarChart3 },
  { href: "/employees", label: "Employees", icon: Users },
];

export function Sidebar() {
  const pathname = usePathname();
  const isEmployeesPage = pathname.startsWith("/employees");

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col overflow-hidden border-r border-sidebar-border bg-sidebar">
      <div className="p-6 border-b border-sidebar-border">
        <Link href="/" className="flex items-center gap-2">
          <Building2 className="h-6 w-6 text-primary" />
          <div>
            <h1 className="font-semibold text-lg leading-tight">ACME Corp</h1>
            <p className="text-xs text-muted-foreground">Salary Management</p>
          </div>
        </Link>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-primary text-sidebar-primary-foreground"
                  : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}

        <div className="pt-3">
          <Link
            href="/employees?add=1"
            className={cn(
              buttonVariants({ variant: "default", size: "sm" }),
              "w-full justify-center shadow-sm",
              isEmployeesPage && "ring-2 ring-primary/20"
            )}
          >
            <UserPlus className="h-4 w-4" />
            Add Employee
          </Link>
        </div>
      </nav>

      <div className="p-4 border-t border-sidebar-border">
        <p className="text-xs text-muted-foreground">HR Manager Portal</p>
      </div>
    </aside>
  );
}
