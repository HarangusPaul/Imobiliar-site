"use client";

import type { Route } from "next";
import Link from "next/link";
import { useState } from "react";

import { Popover } from "@/components/ui/Popover";

import styles from "./CollectionView.module.css";

interface SortMenuProps {
  current: string;
  items: Array<{ label: string; href: Route; active: boolean }>;
}

export function SortMenu({ current, items }: SortMenuProps) {
  const [open, setOpen] = useState(false);

  return (
    <Popover
      open={open}
      onOpenChange={setOpen}
      align="end"
      triggerClassName={styles.sortTrigger}
      trigger={<>Sort by: {current} ↓</>}
    >
      <ul className={styles.sortList}>
        {items.map((item) => (
          <li key={item.href}>
            <Link
              href={item.href}
              scroll={false}
              className={`${styles.sortItem} ${item.active ? styles.sortItemActive : ""}`}
              aria-current={item.active ? "true" : undefined}
              onClick={() => setOpen(false)}
            >
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
    </Popover>
  );
}
