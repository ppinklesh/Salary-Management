"use client";

import { Rectangle, type BarShapeProps } from "recharts";
import { chartBarColor } from "@/lib/chart-colors";

type PayloadWithColorIndex = {
  colorIndex: number;
};

export function ColoredBarShape(props: BarShapeProps) {
  const colorIndex = (props.payload as PayloadWithColorIndex).colorIndex;
  return <Rectangle {...props} fill={chartBarColor(colorIndex)} />;
}
