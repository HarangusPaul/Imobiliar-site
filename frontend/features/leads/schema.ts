import { z } from "zod";

import { optionalEmail, phoneNumber } from "@/lib/validation/schemas";

export const leadSchema = z
  .object({
    full_name: z.string().trim().min(2, "Tell us your name.").max(160),
    phone_number: phoneNumber,
    email: optionalEmail.optional(),
    message: z.string().trim().max(4000).optional(),
    contact_preference: z.enum(["phone", "sms", "email", "any"]).default("any"),
    preferred_time: z.string().trim().max(120).optional(),
    property_slug: z.string().optional(),
    development_slug: z.string().optional(),
    source_path: z.string().optional(),
    website: z.string().max(0).optional(),
  })
  .refine(
    (values) => Boolean(values.message || values.property_slug || values.development_slug),
    { path: ["message"], message: "Tell us what you are looking for." },
  );

export type LeadValues = z.infer<typeof leadSchema>;
