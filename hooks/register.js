// Mod half of agile-dev's Bash permission auto-approval.
//
// permission-gate.sh (wired via the "hooks" key in hooks.json, next to this
// file) still runs first, still works for Manual-mode-style prompting, and
// is still the only protection on a pre-mods Claude Code version. But its
// "allow" decision is not documented to skip auto mode's background
// classifier review — only an explicit permission rule or a mod's
// `tool.check` handler is (code.claude.com/docs/en/permissions.md#extend-permissions-with-hooks).
// `tool.check` fires one step later in the chain, after permission rules and
// settings hooks have already decided, and an explicit allow returned here
// DOES skip the classifier. This file re-decides the same guards.json policy
// at that point. See:
// https://code.claude.com/docs/en/plugins/mods/events.md#approve-or-refuse-a-tool-call-before-the-user-is-asked
//
// Design rule — read this before changing anything below: this file must
// never loosen an inherited "deny". It only (a) independently re-applies
// guards.json's deny patterns as a second, redundant safety net, and
// (b) upgrades an inherited "ask" to "allow" for commands guards.json
// already recognises as safe. It never touches an inherited "allow" or
// "deny" otherwise.
//
// Requires Claude Code v2.1.287+ (mods). On an older version this module
// simply never loads — permission-gate.sh alone still applies, same as
// before this file existed.
//
// Scope note: there is no Write/Edit equivalent of this file. Auto mode
// already auto-approves file edits inside the working directory at an
// earlier step than the classifier (see "Read-only actions and file edits
// in your working directory are auto-approved" in permission-modes.md's
// decision order), so write-guard.sh's allow side needs no mod. Its deny
// side (blocking credential-looking files) is already enforced by the
// settings-hook deny-first precedence, independent of classifier review.
// Porting it here would duplicate logic that already works.

let guardsCache = null

async function loadGuards($) {
  if (guardsCache) return guardsCache
  let deny = []
  let allow = new Set()
  try {
    const raw = await $.fs.read($.plugin.root + '/hooks/guards.json')
    const cfg = JSON.parse(raw)
    deny = (cfg.bash_deny || [])
      .map((pattern) => {
        try {
          return new RegExp(pattern)
        } catch {
          return null // an invalid pattern is skipped, not fatal to the rest
        }
      })
      .filter(Boolean)
    allow = new Set(cfg.bash_allow_tools || [])
  } catch {
    // guards.json missing or unreadable — fail safe: no extra allow, no
    // extra deny. The settings hook's own decision still applies unchanged.
  }
  guardsCache = { deny, allow }
  return guardsCache
}

// Mirrors permission-gate.sh's segment-by-segment check: every
// &&/||/;/| -separated segment must lead with a recognised tool name (after
// stripping leading FOO=bar env assignments), and `git push` is never
// auto-allowed here regardless of which tool list it appears in.
function isRecognisedDevCommand(cmd, allowSet) {
  const segments = cmd.split(/&&|\|\||;|\|/)
  let ok = true
  let sawAnySegment = false
  for (const rawSegment of segments) {
    const seg = rawSegment.trim()
    if (!seg) continue
    sawAnySegment = true
    const toks = seg.split(/\s+/)
    let i = 0
    while (i < toks.length && /^[A-Za-z_][A-Za-z0-9_]*=/.test(toks[i])) i++
    if (i >= toks.length) {
      ok = false
      break
    }
    const tool = toks[i]
    const base = tool.split('/').pop()
    const sub = toks[i + 1] || ''
    if (base === 'git' && sub === 'push') {
      ok = false
      break
    }
    if (allowSet.has(tool) || allowSet.has(base)) continue
    ok = false
    break
  }
  return sawAnySegment && ok
}

export function register(on) {
  on('tool.check', { tool: 'Bash' }, async ($, e, next) => {
    const cmd = (e.input && e.input.command) || ''
    const guards = await loadGuards($)

    // Independent deny re-check, regardless of what next(e) will decide.
    // Redundant with permission-gate.sh by design — never remove this.
    for (const pattern of guards.deny) {
      if (pattern.test(cmd)) {
        return { decision: 'deny', reason: 'Blocked by agile-dev guard (mod): ' + pattern.source }
      }
    }

    const decided = await next(e)
    // Only an inherited "ask" is ours to upgrade. An inherited "allow" or
    // "deny" is left exactly as it came.
    if (decided !== 'ask') return decided

    if (cmd.trim() && isRecognisedDevCommand(cmd, guards.allow)) {
      return { decision: 'allow', reason: 'Recognised dev tool — auto-approved by agile-dev (mod)' }
    }
    return decided
  })
}
