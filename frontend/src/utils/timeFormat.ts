/**
 * SparkMinds AI — 12-Hour Time Display Formatter Utility
 *
 * Converts all 24-hour time strings and time ranges into clear 12-hour AM/PM
 * display format without altering underlying stored schedule values or backend
 * time calculations.
 *
 * Examples:
 * - "18:00"           -> "6:00 PM"
 * - "18:45"           -> "6:45 PM"
 * - "08:30"           -> "8:30 AM"
 * - "12:00"           -> "12:00 PM"
 * - "00:30"           -> "12:30 AM"
 * - "18:00 - 18:45"   -> "6:00 PM - 6:45 PM"
 * - "11:30 - 12:15"   -> "11:30 AM - 12:15 PM" (crosses AM -> PM)
 * - "23:30 - 00:15"   -> "11:30 PM - 12:15 AM" (crosses PM -> AM)
 */

/**
 * Converts a single 24-hour "HH:MM" token into 12-hour "h:mm AM/PM" format.
 */
export function convertSingle24HourTo12Hour(
  hours24: number,
  minutesStr: string
): string {
  const normalizedHours = ((hours24 % 24) + 24) % 24;
  const period = normalizedHours >= 12 ? 'PM' : 'AM';
  const hours12 = normalizedHours % 12 === 0 ? 12 : normalizedHours % 12;
  const paddedMinutes = minutesStr.padStart(2, '0');
  return `${hours12}:${paddedMinutes} ${period}`;
}

/**
 * Formats any string containing 24-hour times or time ranges into 12-hour AM/PM format.
 * Preserves all surrounding text, separators (" - ", "–", " to "), and handles
 * ranges that cross from AM to PM or PM to AM.
 * Also normalizes shorthand hour labels like "6 AM" -> "6:00 AM".
 */
export function formatTime12Hour(input?: string | null): string {
  if (!input) return '';

  // 1. Convert all 24-hour HH:MM tokens that are not already followed by AM/PM
  const withConverted24h = input.replace(
    /\b([01]?\d|2[0-3]):([0-5]\d)\b(?!\s*[AaPp][Mm]\b)/g,
    (_match, hStr: string, mStr: string) => {
      const hours = parseInt(hStr, 10);
      return convertSingle24HourTo12Hour(hours, mStr);
    }
  );

  // 2. Normalize standalone hour shorthand like "6 AM" or "9 PM" to "6:00 AM" / "9:00 PM"
  return withConverted24h.replace(
    /\b(1[0-2]|[1-9])\s*([AaPp][Mm])\b/g,
    (_match, hStr: string, ampm: string) => `${hStr}:00 ${ampm.toUpperCase()}`
  );
}

/**
 * Alias for formatting schedule time slots and ranges (e.g., "18:00 - 18:45" -> "6:00 PM - 6:45 PM").
 */
export function formatTimeRange12Hour(timeSlot?: string | null): string {
  return formatTime12Hour(timeSlot);
}

/**
 * Formats an ISO-8601 timestamp or date-time string into a 12-hour time string (e.g., "6:30 PM").
 */
export function formatIsoTimestamp12Hour(isoString?: string | null): string {
  if (!isoString) return '';
  // Check if there is an explicit HH:MM inside the string
  const timeMatch = isoString.match(/T([01]\d|2[0-3]):([0-5]\d)/);
  if (timeMatch) {
    return convertSingle24HourTo12Hour(
      parseInt(timeMatch[1], 10),
      timeMatch[2]
    );
  }
  return formatTime12Hour(isoString);
}

/**
 * Formats a homework deadline and reminder display in 12-hour AM/PM format
 * without altering the stored due_date string.
 */
export function formatHomeworkDeadline12Hour(
  dueDate: string,
  priority?: 'High' | 'Medium' | 'Low' | string
): {
  dueDisplay: string;
  reminderDisplay: string;
} {
  const hasExplicitTime = /\b([01]?\d|2[0-3]):([0-5]\d)\b/.test(dueDate);
  const dueTime24 =
    priority === 'High' ? '18:00' : priority === 'Medium' ? '19:30' : '20:30';
  const reminderTime24 =
    priority === 'High' ? '16:30' : priority === 'Medium' ? '17:30' : '18:30';

  const dueDisplay = hasExplicitTime
    ? formatTime12Hour(dueDate)
    : `${dueDate}, ${formatTime12Hour(dueTime24)}`;

  const reminderDisplay = formatTime12Hour(reminderTime24);

  return { dueDisplay, reminderDisplay };
}

/**
 * Formats an exam schedule date and session window in 12-hour AM/PM format
 * without altering the stored exam_date string.
 */
export function formatExamSchedule12Hour(
  examDate: string,
  slot24 = '09:30 - 11:00'
): string {
  const hasExplicitTime = /\b([01]?\d|2[0-3]):([0-5]\d)\b/.test(examDate);
  if (hasExplicitTime) {
    return formatTime12Hour(examDate);
  }
  return `${examDate} (${formatTime12Hour(slot24)})`;
}

/**
 * Formats a spaced-repetition revision date with a 12-hour AM/PM scheduled review time
 * without altering the stored next_review_date string.
 */
export function formatRevisionSchedule12Hour(
  nextReviewDate: string,
  slot24 = '17:30'
): string {
  const hasExplicitTime = /\b([01]?\d|2[0-3]):([0-5]\d)\b/.test(nextReviewDate);
  if (hasExplicitTime) {
    return formatTime12Hour(nextReviewDate);
  }
  return `${nextReviewDate} at ${formatTime12Hour(slot24)}`;
}

