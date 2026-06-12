"use client";

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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useState } from "react";
import { EmployeeOffboardData, EXIT_REASONS, type ExitReason } from "@/lib/api";

type Props = Readonly<{
  open: boolean;
  onOpenChange: (open: boolean) => void;
  employeeName: string;
  onConfirm: (data: EmployeeOffboardData) => void;
}>;

type OffboardDialogBodyProps = Readonly<{
  onConfirm: (data: EmployeeOffboardData) => void;
  onCancel: () => void;
}>;

const REASON_LABELS: Record<ExitReason, string> = {
  terminated: "Terminated",
  resigned: "Resigned",
  retired: "Retired",
  layoff: "Layoff",
  end_of_contract: "End of Contract",
  other: "Other",
};

function isExitReason(value: string): value is ExitReason {
  return (EXIT_REASONS as readonly string[]).includes(value);
}

function todayIsoDate(): string {
  return new Date().toISOString().split("T")[0];
}

function OffboardDialogBody({ onConfirm, onCancel }: OffboardDialogBodyProps) {
  const [exitDate, setExitDate] = useState(todayIsoDate);
  const [exitReason, setExitReason] = useState<ExitReason>("resigned");

  return (
    <>
      <div className="space-y-4 py-2">
        <div>
          <Label htmlFor="exit_date">Exit Date</Label>
          <Input
            id="exit_date"
            type="date"
            value={exitDate}
            onChange={(e) => setExitDate(e.target.value)}
          />
        </div>
        <div>
          <Label>Exit Reason</Label>
          <Select
            value={exitReason}
            onValueChange={(v) => {
              if (v && isExitReason(v)) setExitReason(v);
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select reason" />
            </SelectTrigger>
            <SelectContent>
              {EXIT_REASONS.map((reason) => (
                <SelectItem key={reason} value={reason}>
                  {REASON_LABELS[reason]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button
          variant="destructive"
          onClick={() => onConfirm({ exit_date: exitDate, exit_reason: exitReason })}
          disabled={!exitDate || !exitReason}
        >
          Offboard
        </Button>
      </DialogFooter>
    </>
  );
}

export function OffboardDialog({
  open,
  onOpenChange,
  employeeName,
  onConfirm,
}: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Offboard Employee</DialogTitle>
          <DialogDescription>
            Record the departure of <strong>{employeeName}</strong>. The employee
            record will be kept for history — it will not be deleted.
          </DialogDescription>
        </DialogHeader>

        {open ? (
          <OffboardDialogBody
            key={employeeName}
            onConfirm={onConfirm}
            onCancel={() => onOpenChange(false)}
          />
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
