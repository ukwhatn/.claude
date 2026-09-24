/**
 * The heading the section is found under, any level, any case, indented up
 * to three spaces as CommonMark allows.
 */
const HEADING = /^ {0,3}(#{1,6})[ \t]+compact instructions(?:[ \t]+#+)?[ \t]*$/i

const ANY_HEADING = /^ {0,3}(#{1,6})(?:[ \t]|$)/

const FENCE = /^ {0,3}(`{3,}|~{3,})/

/**
 * The body of the first "Compact Instructions" section of a Markdown text:
 * the lines under its heading up to the next heading of the same or a higher
 * level, trimmed.
 *
 * Headings inside fenced code blocks are not headings.
 *
 * @param markdown the file's text
 * @returns the section's body, or undefined when there is none or it is empty
 */
export function compactInstructionsOf(markdown: string): string | undefined {
  const lines = markdown.split(/\r?\n/)
  let level: number | undefined
  let fence: string | undefined
  const body: string[] = []

  for (const line of lines) {
    const isFenced = fence !== undefined
    fence = fenceAfter(fence, line)

    if (level === undefined) {
      const found = isFenced || fence !== undefined ? null : HEADING.exec(line)
      level = found?.[1]?.length

      continue
    }

    const heading = isFenced || fence !== undefined ? null : ANY_HEADING.exec(line)

    if (heading?.[1] !== undefined && heading[1].length <= level) {
      break
    }

    body.push(line)
  }

  const text = body.join('\n').trim()

  return text === '' ? undefined : text
}

/**
 * The fence open after `line`: a fence closes only on a bare run of its own
 * character at least as long as the one that opened it.
 */
function fenceAfter(open: string | undefined, line: string): string | undefined {
  const run = FENCE.exec(line)?.[1]

  if (open === undefined) {
    return run
  }

  const closes =
    run !== undefined &&
    run[0] === open[0] &&
    run.length >= open.length &&
    line.trim() === run

  return closes ? undefined : open
}

/**
 * What a compaction is told: the section first, then what the person typed
 * after /compact, when anything.
 *
 * @param section the Compact Instructions section
 * @param typed the instructions the compaction already carries
 * @returns the joined instructions
 */
export function joinedInstructions(
  section: string,
  typed: string | undefined,
): string {
  const extra = typed?.trim()

  return extra === undefined || extra === '' ? section : `${section}\n\n${extra}`
}
