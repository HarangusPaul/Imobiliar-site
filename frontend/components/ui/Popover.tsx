"use client";

import { useEffect, useId, useRef, type ReactNode } from "react";

import styles from "./Popover.module.css";

/**
 * A trigger button with a panel below it. Closes on outside click and Escape.
 * Open state is owned by the caller so a selection can close it.
 */

interface PopoverProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  trigger: ReactNode;
  triggerClassName?: string;
  align?: "start" | "end";
  children: ReactNode;
}

export function Popover({
  open,
  onOpenChange,
  trigger,
  triggerClassName,
  align = "start",
  children,
}: PopoverProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const panelId = useId();

  useEffect(() => {
    if (!open) return;
    const onPointer = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) onOpenChange(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onOpenChange(false);
    };
    document.addEventListener("pointerdown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, [open, onOpenChange]);

  return (
    <div ref={rootRef} className={styles.root}>
      <button
        type="button"
        className={triggerClassName}
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => onOpenChange(!open)}
      >
        {trigger}
      </button>
      <div
        id={panelId}
        className={`${styles.panel} ${align === "end" ? styles.end : ""}`}
        hidden={!open}
      >
        {children}
      </div>
    </div>
  );
}
