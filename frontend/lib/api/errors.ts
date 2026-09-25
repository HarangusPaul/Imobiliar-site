/**
 * Translating the backend error envelope into something the UI can act on.
 *
 * The backend always fails in one shape (see `core/api/exceptions.py`):
 *
 *   { "error": { "code", "message", "details"?, "request_id" } }
 *
 * so this is the only place that needs to know it.
 */

export interface FieldErrors {
  [field: string]: string[];
}

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly details: unknown;
  readonly requestId: string;

  constructor(init: {
    code: string;
    message: string;
    status: number;
    details?: unknown;
    requestId?: string;
    cause?: unknown;
  }) {
    super(init.message, { cause: init.cause });
    this.name = "ApiError";
    this.code = init.code;
    this.status = init.status;
    this.details = init.details;
    this.requestId = init.requestId ?? "";
  }

  get isValidation(): boolean {
    return this.code === "validation_error";
  }

  get isUnauthenticated(): boolean {
    return this.status === 401 || this.code === "not_authenticated";
  }

  get isForbidden(): boolean {
    return this.status === 403;
  }

  get isNotFound(): boolean {
    return this.status === 404;
  }

  /**
   * Field-level messages for a form, or `null` when the failure was not a
   * validation error. Forms bind this directly; they never inspect `details`.
   */
  fieldErrors(): FieldErrors | null {
    if (!this.isValidation || typeof this.details !== "object" || this.details === null) {
      return null;
    }
    const result: FieldErrors = {};
    for (const [field, value] of Object.entries(this.details as Record<string, unknown>)) {
      result[field] = Array.isArray(value) ? value.map(String) : [String(value)];
    }
    return result;
  }
}

export function parseErrorBody(payload: unknown, status: number): ApiError {
  const error =
    payload && typeof payload === "object" && "error" in payload
      ? (payload as { error: Record<string, unknown> }).error
      : null;

  return new ApiError({
    code: String(error?.code ?? "error"),
    message: String(error?.message ?? "Something went wrong."),
    status,
    details: error?.details,
    requestId: String(error?.request_id ?? ""),
  });
}

export function isApiError(value: unknown): value is ApiError {
  return value instanceof ApiError;
}
