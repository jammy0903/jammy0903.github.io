---
layout: post
title: "CodeInsight Tech Stack — Why React 19, Fastify, and Docker Sandbox"
date: 2026-02-27 20:00:00 +0900
categories: blog
tags: ['react', 'fastify', 'docker', 'architecture', 'tech-stack']
---

This is Part 2 of the CodeInsight series. [Part 1: Why I Built It](/2026-02-27-I-Built-a-Code-Visualization-Platform/)

---

## Architecture Overview

CodeInsight is a TypeScript monorepo with four packages:

```
packages/
├── frontend/     → React 19 + Vite (UI & visualizations)
├── backend/      → Node.js + Fastify (API & auth)
├── shared/       → Zod schemas & types
└── simulators/   → Per-language code execution engines
```

The data flow is straightforward:

**Code Input → Simulator → Execution Trace (JSON) → Visualization**

In Lesson mode, the execution trace is pre-built as JSON files. In Playground mode, user code runs inside a Docker container that generates the trace dynamically.

---

## Frontend: React 19 + Vite

### Why React 19

React 19's improved performance and the ecosystem maturity made it the obvious choice. The visualization components are heavily interactive — variables animating, stack frames growing, pointers connecting — and React handles this well with its reconciliation model.

### State Management: Zustand over Redux

I evaluated three options:

| | Redux | Context | **Zustand** |
|---|---|---|---|
| Boilerplate | Heavy | Light | **Minimal** |
| DevTools | Yes | No | **Yes** |
| Performance | Good | Re-render issues | **Selective subscriptions** |
| Learning curve | Steep | Low | **Low** |

Zustand won because it offers Redux-like capabilities with almost zero boilerplate. A single store file manages auth state, lesson progress, and UI preferences.

### TailwindCSS

No regrets. Utility-first CSS keeps styling co-located with components and eliminates the "where does this style come from" problem. Combined with CSS custom properties for theming (dark/light mode), it just works.

### Vite

After migrating from Create React App, build times went from ~45 seconds to ~3 seconds. Hot Module Replacement is nearly instant. There's no going back.

---

## Backend: Fastify + Prisma

### Why Fastify over Express

Express is the default choice, but Fastify offers measurable advantages:

- **2-3x faster** in benchmarks (thanks to schema-based serialization)
- **Built-in validation** with JSON Schema (we use Zod + fastify-type-provider-zod)
- **Plugin system** that encourages clean architecture
- **TypeScript-first** with excellent type inference

### Prisma ORM

Prisma handles the PostgreSQL layer. The schema-as-code approach means database structure is version-controlled alongside application code. Migrations are deterministic and reviewable.

The tradeoff: Prisma generates large client bundles and complex queries can be slower than raw SQL. For our use case (mostly simple CRUD with some joins), the developer experience wins.

### Zod for Validation

Every API input is validated with Zod schemas that live in the `shared` package. The same schemas validate on both frontend (form inputs) and backend (request bodies). Single source of truth.

---

## Simulators: Docker Sandbox

This is the most critical and complex piece. When a user writes `system("rm -rf /")` in the playground, we need to:

1. Execute it safely
2. Capture the execution trace
3. Return meaningful visualization data

Each language has its own simulator:
- **C**: Parses AST, simulates memory operations (stack/heap allocation)
- **JavaScript**: Traces execution context, scope chain, event loop
- **Java**: Models JVM memory (method area, heap, stack frames)
- **Python**: Tracks reference graph and name bindings

Playground mode wraps everything in Docker containers with strict isolation. More on this in [Part 3: Docker Sandbox Security](/2026-02-27-CodeInsight-Docker-Security/).

---

## Infrastructure

### Render

The entire stack runs on Render:
- **Frontend**: Static site deployment (build + CDN)
- **Backend**: Docker web service with auto-scaling
- **Database**: Managed PostgreSQL

Push to `main` triggers automatic deployment. Frontend builds in ~2 minutes, backend in ~5-10 minutes (including Prisma migrations and seeding).

### Content Architecture: DB + JSON Hybrid

A key architectural decision: lesson **metadata** lives in PostgreSQL, but lesson **content** (code, steps, explanations) lives in JSON files loaded into memory at startup.

Why the split:
- JSON content lookups are ~100x faster than DB queries (0.1ms vs 5-20ms)
- Content is version-controlled in Git
- Structure (what lessons exist) stays in DB for relational queries
- Content (what each lesson teaches) stays in JSON for fast reads

---

## Lessons Learned

1. **Start with the simplest thing that works.** The first version had no Docker — just a regex-based code validator. It was insecure but shipped fast.

2. **Monorepo from day one.** Sharing types between frontend and backend eliminated an entire category of bugs.

3. **Don't optimize prematurely.** The JSON content cache was added after profiling showed DB reads were the bottleneck. Not before.

---

*Next up: [Part 3 — Docker Sandbox Security](/2026-02-27-CodeInsight-Docker-Security/)*

**Links:** [Live Demo](https://codeinsight.online) | [GitHub](https://github.com/jammy0903/CodeInsight)
