/**
 * The heading the section is found under, any level, any case.
 */
const HEADING = /^(#{1,6})[ \t]+compact instructions[ \t]*#*[ \t]*$/i

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
  let isInFence = false
  const body: string[] = []

  for (const line of lines) {
    if (/^\s*(```|~~~)/.test(line)) {
      isInFence = !isInFence
    }

    const heading = isInFence ? undefined : /^(#{1,6})[ \t]/.exec(line)

    if (level === undefined) {
      const found = isInFence ? null : HEADING.exec(line)
      level = found?.[1]?.length

      continue
    }

    if (heading?.[1] !== undefined && heading[1].length <= level) {
      break
    }

    body.push(line)
  }

  const text = body.join('\n').trim()

  return text === '' ? undefined : text
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
