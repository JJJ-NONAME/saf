const BLOCKED_CHARS = /[!@#$%^&*()=+><]/;
const BLOCKED_CHARS_DISPLAY = "!@#$%^&*()=+><";

export function validateProjectName(name: string): string {
  if (BLOCKED_CHARS.test(name)) {
    return `Project name cannot contain special characters: ${BLOCKED_CHARS_DISPLAY}`;
  }
  return "";
}
