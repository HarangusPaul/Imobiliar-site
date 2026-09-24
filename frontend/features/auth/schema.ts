import { z } from "zod";

import { optionalEmail, password, phoneNumber } from "@/lib/validation/schemas";

/**
 * The account identifier is a phone number. There is no username and no email
 * login, matching `apps/accounts`.
 */
export const loginSchema = z.object({
  phone_number: phoneNumber,
  password: z.string().min(1, "Enter your password."),
});

export const registerSchema = z.object({
  phone_number: phoneNumber,
  password,
  first_name: z.string().trim().max(80).optional(),
  last_name: z.string().trim().max(80).optional(),
  email: optionalEmail.optional(),
});

export type LoginValues = z.infer<typeof loginSchema>;
export type RegisterValues = z.infer<typeof registerSchema>;
