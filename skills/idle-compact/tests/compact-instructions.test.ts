import { describe, expect, test, tier } from 'claude-code/testing'

import { compactInstructionsOf, joinedInstructions } from '../hooks/compact-instructions.js'

tier('user')

describe('compact-instructions', () => {
  test('the section ends at the next heading of the same level', async () => {
    expect(
      compactInstructionsOf('## A\na\n## Compact Instructions\nkeep x\n### sub\nkeep y\n## B\nb'),
    ).toBe('keep x\n### sub\nkeep y')
  })

  test('any heading level and case, CJK body kept as is', async () => {
    expect(compactInstructionsOf('# compact instructions\n\n稼働中のサブエージェントを保持する\n')).toBe(
      '稼働中のサブエージェントを保持する',
    )
  })

  test('a heading inside a code fence is not the section', async () => {
    expect(compactInstructionsOf('```\n## Compact Instructions\nfake\n```\n')).toBeUndefined()
  })

  test('a missing or empty section is undefined', async () => {
    expect(compactInstructionsOf('')).toBeUndefined()
    expect(compactInstructionsOf('## Compact Instructions\n\n## Next\n')).toBeUndefined()
  })

  test('typed instructions follow the section; blank ones are dropped', async () => {
    expect(joinedInstructions('s', 'keep logs')).toBe('s\n\nkeep logs')
    expect(joinedInstructions('s', '  ')).toBe('s')
    expect(joinedInstructions('s', undefined)).toBe('s')
  })
})
