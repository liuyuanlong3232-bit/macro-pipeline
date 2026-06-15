# Chinese Community "Five Slots" → Real Hermes Features

Mapping of the popular Chinese community "五个插槽五大核心系统" framework to actual Hermes Agent features.

## Overview

The "five slots" framework is a **conceptual/teaching tool** created by the Chinese Hermes community to explain Hermes capabilities through architectural metaphor. It is NOT an installable modular system — there are no "slots" in the codebase.

However, every system it describes maps to real configurable features.

---

## Slot 1: 身份系统 (Soul / Identity)

| Claimed | Reality |
|---------|---------|
| "soul.md 配置身份信息" | ✅ **`~/.hermes/SOUL.md`** — real feature. Injected as slot #1 in system prompt. |
| "211 套中文角色模板" | ❌ Not official. Hermes ships 14 built-in personalities via `/personality`. Community has additional templates outside the official repo. |
| "可直接选用骨架" | ⚠️ Partial. Built-in personalities: helpful, concise, technical, creative, teacher, kawaii, catgirl, pirate, shakespeare, surfer, noir, uwu, philosopher, hype. Custom personalities via `config.yaml agent.personalities`. |

**Install status**: Not a plugin — edit `~/.hermes/SOUL.md` directly. Use `/personality name` to switch temporarily.

---

## Slot 2: 记忆系统 (Memory)

| Claimed | Reality |
|---------|---------|
| "Palace 对话归档与全文搜索" | ⚠️ Partial. Hermes stores sessions in SQLite + FTS5. There is no "Palace" module name. The actual query tool is `session_search()` (FTS5-backed). |
| "llm-wiki 知识沉淀" | ✅ Exists as a built-in skill under `research` category. Karpathy's LLM Wiki pattern. |
| "gbrain 结构化知识图谱" | ❌ Not a Hermes feature. GBrain (github.com/garrytan/gbrain) is a **separate standalone project** by Garry Tan — Docker-based personal knowledge graph with entity extraction, hybrid search, auto-maintenance. Connects to Hermes via MCP HTTP. |
| "session_search 跨层检索" | ✅ **Built-in tool** `session_search()`. Real FTS5 search over past conversations. |

**Install status**:
- `session_search` — already available as a tool
- llm-wiki — built-in skill, already loaded
- GBrain — requires Docker + MCP HTTP setup (see github.com/garrytan/gbrain)

---

## Slot 3: 感知能力 (Perception)

| Claimed | Reality |
|---------|---------|
| "网页抓取、搜索" | ✅ `web_search`, `web_extract`, `browser_*` tools — built-in |
| "Jina Reader" | ✅ External service. Configurable via custom provider. |
| "Crow for AI" | ✅ External service. Configurable via custom provider. |
| "表格分析等" | ✅ Can process tables via web_extract or terminal tools. |

**Install status**: Already built-in. Enable/disable via `hermes tools`.

---

## Slot 4: 表达能力 (Expression)

| Claimed | Reality |
|---------|---------|
| "Whisper 语音转文字 99种语言" | ✅ Real. STT provider chain: local (faster-whisper) → Groq → OpenAI → Mistral. Configure via `stt.*` in config. |
| "TTS 文字转语音" | ✅ Real. `/voice on/off/tts`. Providers: Edge (free), ElevenLabs, OpenAI, MiniMax, Mistral, NeuTTS. |
| "图片生成（对接三家引擎）" | ✅ Real. `image_gen` toolset. Three engines via Nous Portal or custom providers. |

**Install status**: Already available. Needs API keys or `hermes setup --portal` for bundled access.

---

## Slot 5: 效率与进化 (Efficiency & Evolution)

| Claimed | Reality |
|---------|---------|
| "RTK 技术减少 80%-90% Token 消耗" | ❌ Not real. No "RTK technology" exists. Hermes has context compression (`compression.*` config) with configurable threshold/target_ratio. |
| "遗传算法根据使用习惯自动进化" | ⚠️ Partial. No built-in genetic algorithm. But: (1) **Skills system** — Hermes auto-creates and refines skills from experience (the real "learning loop"). (2) **Curator** — autonomous skill cleanup, consolidation, archiving. (3) **hermes-agent-self-evolution** (github.com/NousResearch/hermes-agent-self-evolution) — separate official project using DSPy + GEPA for genetic optimization of skills, not built-in. Costs $2-10/run via API. |
| "配置顺序建议：先身份→记忆→感知→表达→效率" | ✅ **Good advice.** Practical order: SOUL.md first (core identity), then memory (persist learning), then tools (perception = web/browser), then voice/media (expression), then compression (efficiency). Not official but sensible. |

---

## Summary: What's Installable vs. What's Conceptual

| "Slot" component | Type | Can install? |
|---|---|---|
| SOUL.md | Official feature | Just edit the file |
| /personality | Official feature | Built-in |
| session_search | Official tool | Already available |
| llm-wiki | Built-in skill | Already available |
| web_search / web_extract | Official tools | Enable via hermes tools |
| STT / TTS / image_gen | Official features | Configure provider |
| Compression | Official feature | `hermes config set` |
| Skills / Curator | Official features | Built-in |
| GBrain | Standalone project | Needs Docker + MCP |
| G-Stack | Hub skill + standalone toolkit | `hermes skills install` OR git clone + bun |
| Hermes WebUI | Standalone web app | git clone + python app.py |
| Hermes Studio | Standalone web app | `npm install -g hermes-web-ui` |
| Hermes Self-Evolution | Standalone tool | git clone + pip install |
| awesome-hermes-agent | README resource list | Not installable |
| Self-Evolution | Standalone project | Needs git clone + pip install |
| "Palace" | Community name for session store | Not a separate install |
| "RTK" / "遗传算法" | Community embellishments | Do not exist |
| "211 套模板" | Community resource | Not official Hermes |
