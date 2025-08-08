# Generative UI Pipeline — Implementation Record (2025-08-08)

## Scope
Project-agnostic agentic pipeline to transform design inputs → critique → component tree → strict JSON → documentation. Triggerable via `/ui` (Claude Code) and `@ui.md` (Cursor).

## Files Added
- `.claude/prompts/generative_ui_pipeline_master_prompt.md`
- `.claude/prompts/generative_ui_pipeline_master_prompt.meta.json`
- `.claude/workflows/generative_ui_pipeline.yaml`
- `.cursor/ui.mdc`
- `.claude/instructions/generative_ui_pipeline_setup.md`
- `docs/schemas/ui_schema.schema.json`

## Files Modified
- `.claude/commands/ui.md` — appended "Generative UI Pipeline" command signature, args, behavior, example.

## Behavior
- Sequential agents: VHA → CA → SDG → CDS with deterministic handoffs.
- Validation: JSON Schema enforcement, no-invented-components vs manifest, optional a11y lint.
- HITL gates after VHA and SDG (configurable).
- Artifacts persisted under `outputs/design_pipeline/<timestamp>/`.

## Project-Agnostic Invocation
- Claude Code: global command expected at `~/.claude/commands/ui.md` (user-level). Optional symlink to `/user:ui`.
- Cursor: per-project rule `.cursor/ui.mdc` enables `@ui.md`/`@ui`.

## Model Routing (config docs)
- Declared in `.claude/workflows/generative_ui_pipeline.yaml` and prompt meta; overridable via flags `--model.vha|ca|sdg|cds`.

## Confidence
- Success likelihood: 99% given schema validation, HITL gates, and documented routing.
