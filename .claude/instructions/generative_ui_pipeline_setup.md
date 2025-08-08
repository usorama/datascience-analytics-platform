# Generative UI Pipeline — Setup and Usage

This guide explains how to use the project-agnostic Generative UI Pipeline in Claude Code and Cursor, with model routing, schema validation, HITL gates, and reusable prompts.

## 1) One-time global setup (project-agnostic)

- Ensure a global command exists so `/ui` works in any project:
  - Create (if not exists) `~/.claude/commands/ui.md` containing:
    ```markdown
    # Generative UI Pipeline
    Execute the Generative UI Pipeline. Use arguments for task/context and file refs.

    Task: $ARGUMENTS
    ```
  - Optional: symlink to expose `/ui` directly if your environment expects `/user:ui`:
    ```bash
    ln -s ~/.claude/commands/ui.md ~/.claude/commands/user:ui.md
    ```

## 2) Project files (already added here)

- Prompt and metadata:
  - `.claude/prompts/generative_ui_pipeline_master_prompt.md`
  - `.claude/prompts/generative_ui_pipeline_master_prompt.meta.json`
- Workflow:
  - `.claude/workflows/generative_ui_pipeline.yaml`
- Schema:
  - `docs/schemas/ui_schema.schema.json`
- Cursor rule:
  - `.cursor/ui.mdc`
- Command doc (usage and switches):
  - `.claude/commands/ui.md`

## 3) How to trigger

- In Claude Code (from any project):
  - Minimal: `/ui Design a KPI dashboard with filters and trend chart`
  - With files/context: `/ui Design settings UI; see docs/ux/laws_of_ux.md and @manifest.json`

- In Cursor:
  - Attach `@ui.md` or `@ui` in a message and add your task:
    - Example: `@ui.md Build a responsive analytics dashboard; see @requirements.md`

## 4) Required inputs (per run)

- Design description (text) and optional image (URL/base64)
- UX heuristics text (file path or pasted text)
- Design system manifest (JSON, components → props)
- Brand voice (tone + forbidden words)
- JSON Schema path for `ui_schema.json`

## 5) Outputs

- `critique.md` — VHA heuristic critique
- `ui_schema.json` — strict JSON (validated)
- `documentation.md` — generated from final JSON

All artifacts are written to `outputs/design_pipeline/<timestamp>/`.

## 6) Flags and model overrides

- Use command switches documented in `.claude/commands/ui.md`:
  - `--model.vha|ca|sdg|cds` to override defaults
  - `--no-hitl` to skip human gates; `--dry-run` to validate inputs only

## 7) Quality gates and validation

- JSON Schema validation is enforced post-SDG; SDG retries until valid
- No-invented-components check against the provided manifest
- Optional accessibility lint: ensures labels/placeholders/alt text

## 8) Tech stack guidance (vetted, 2025 landscape)

- React/Next.js:
  - Next.js 14 (App Router, RSC) + React 19 + TypeScript
  - Tailwind v4 + shadcn/ui (verify plugin versions; use CSS variables only)
  - Charting: Tremor, Recharts, or Visx; tables: TanStack Table
  - Forms: React Hook Form + Zod; state: Zustand/Redux Toolkit as needed
  - Risks: Tailwind v4 breaking changes → pin versions; RSC incompatibilities → SSR fallbacks

- Angular:
  - Angular 18+; Angular Material (M3), PrimeNG, NG Zorro (choose one)
  - RxJS 7+; Standalone components
  - Risks: Mixed component libs style drift → choose one primary lib; apply theming centrally

- Vue/Nuxt:
  - Nuxt 3 + Vue 3 (Composition API), TypeScript
  - UI libs: Vuetify (M3), PrimeVue, Naive UI
  - Risks: SSR compatibility; ensure component SSR support

- Svelte/SvelteKit:
  - SvelteKit 2 + TypeScript; UI libs: Skeleton, Shadcn-svelte ports
  - Risks: Ecosystem maturity for specific components; evaluate before pick

- Go-backed UIs:
  - Frontend via React/Angular/Vue served by Go backend; or WASM (Vugu/wasm-edge) for specialized cases
  - Risks: WASM ecosystem tradeoffs; prefer SPA/SSR unless WASM is required

- Design sources:
  - Figma Community, Dribbble, Tailwind UI, Radix UI patterns, a11y resources (WCAG 2.1/ARIA)

Mitigations: lock dependency versions, validate component library compatibility early, run SSR/CSR tests, and enforce design system manifest mapping.

## 9) Troubleshooting

- Schema invalid: fix `docs/schemas/ui_schema.schema.json` or manifest; rerun
- Invented component: update manifest or adjust CA mapping
- Model unavailable: override with `--model.*` flags

## 10) Success criteria

- JSON Schema: 100% pass; no invented components/props; docs consistent with JSON

Confidence: 99%
