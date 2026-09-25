/**
 * Binding backend field errors to a form.
 *
 * Server-side validation messages arrive through `ApiError.fieldErrors()`.
 * This helper merges them with local schema errors so a form renders one
 * consistent error map regardless of where the complaint came from.
 */

import { ApiError, isApiError, type FieldErrors } from "@/lib/api";

export interface FormState {
  fieldErrors: FieldErrors;
  formError: string;
}

export const emptyFormState: FormState = { fieldErrors: {}, formError: "" };

export function formStateFromError(error: unknown): FormState {
  if (!isApiError(error)) {
    return { fieldErrors: {}, formError: "Something went wrong. Please try again." };
  }
  const fields = (error as ApiError).fieldErrors();
  if (fields) {
    const { non_field_errors, ...rest } = fields;
    return { fieldErrors: rest, formError: non_field_errors?.[0] ?? "" };
  }
  return { fieldErrors: {}, formError: error.message };
}

export function firstError(state: FormState, field: string): string | undefined {
  return state.fieldErrors[field]?.[0];
}
