/**
 * Shared, domain-neutral validation primitives.
 *
 * Form-specific schemas belong to their feature (`features/leads/schema.ts`,
 * `features/auth/schema.ts`). Only the pieces reused across features live here.
 *
 * Client-side validation is a convenience. Every rule is enforced again by the
 * backend, which is the authority.
 */

import { z } from "zod";

/** Accepts what people actually type; the backend normalises to E.164. */
export const phoneNumber = z
  .string()
  .trim()
  .min(8, "Enter a valid phone number.")
  .max(24, "Enter a valid phone number.")
  .regex(/^[+\d][\d\s\-().]*$/, "Enter a valid phone number.");

export const password = z
  .string()
  .min(8, "Use at least 8 characters.")
  .max(128, "That password is too long.");

export const optionalEmail = z.union([z.literal(""), z.string().email("Enter a valid email.")]);

export const slug = z
  .string()
  .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, "Invalid identifier.");

export const positiveDecimal = z.coerce
  .number()
  .nonnegative("Enter a positive value.")
  .finite();
