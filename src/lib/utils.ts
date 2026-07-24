/**
 * Merge class names. Filters falsy values.
 * Equivalent to clsx but zero-dependency.
 */
export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ");
}
