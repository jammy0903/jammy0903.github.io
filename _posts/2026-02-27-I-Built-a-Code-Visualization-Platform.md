---
layout: post
title: "I Built a Code Visualization Platform Because I Couldn't Understand Pointers"
date: 2026-02-27 19:00:00 +0900
categories: blog
tags: ['open-source', 'side-project', 'coding-education', 'visualization', 'react']
thumbnail-img: https://raw.githubusercontent.com/jammy0903/CodeInsight/main/docs/demo.gif
share-img: https://raw.githubusercontent.com/jammy0903/CodeInsight/main/docs/demo.gif
---

When I was learning C, the hardest part wasn't the syntax. It was understanding **what actually happens when code runs**.

```c
int *p = &x;
```

*What does this even mean?* Where does `x` live in memory? What is `p` pointing to? The textbook diagrams were static and abstract. I needed to **see** it happening.

So I built [**CodeInsight**](https://codeinsight.online) — a free, open-source platform that visualizes code execution step by step.

---

## The Problem

Every CS student hits the same wall:

- **C**: "What's the difference between stack and heap? Why did my pointer crash?"
- **JavaScript**: "Why does `setTimeout(fn, 0)` run after my Promise? What even is the event loop?"
- **Java**: "Where do objects live? What happens when I call `new`?"
- **Python**: "Are lists passed by reference or value?"

Existing tools like Python Tutor are great, but I wanted something that shows **real memory layouts**, not just boxes and arrows. I wanted to see stack frames growing, heap allocations happening, and pointers connecting — in real time, with animations.

---

## What CodeInsight Does

![CodeInsight Demo](https://raw.githubusercontent.com/jammy0903/CodeInsight/main/docs/demo.gif)

CodeInsight takes your code and breaks it down into execution steps. At each step, you can see:

**For C/C++:**
- Full memory layout — Stack, Heap, BSS, DATA, TEXT segments
- Variable allocation and garbage values
- Pointer arrows connecting to their targets
- Stack frames being pushed and popped

**For JavaScript:**
- Event loop visualization (Call Stack, Microtask Queue, Macrotask Queue)
- Scope chain and closures
- Prototype chain
- Promise resolution flow
- `this` binding in different contexts

**For Java:**
- JVM memory model
- Object references on the heap
- Method area and stack frames

**For Python:**
- Reference graph showing how names bind to objects
- Mutable vs immutable object behavior

---

## Two Modes

### 1. Lesson Mode
Guided curriculum with pre-built visualizations. Each lesson has:
- Step-by-step code walkthrough
- AI-powered explanations at each step
- Interactive quizzes to test understanding
- Common misconceptions highlighted

### 2. Playground Mode
Write your own code and watch it execute. The simulator runs your code in a Docker sandbox and generates an execution trace that gets visualized in real time.

---

## The Tech Behind It

For those interested in the implementation:

| Layer | Stack |
|-------|-------|
| Frontend | React 19, Vite, TailwindCSS, Zustand, Framer Motion |
| Backend | Node.js, Fastify, Prisma, PostgreSQL |
| Execution | Docker-sandboxed per-language simulators |
| AI | DeepSeek for step explanations |
| Infra | Render (frontend + backend + DB), pnpm monorepo |

The architecture separates **structure** (database) from **content** (JSON files). Lesson metadata lives in PostgreSQL, while the actual step-by-step content is stored as JSON files loaded into memory at startup — making content lookups ~100x faster than DB queries.

Code execution in Playground mode runs inside Docker containers with strict security:
- `--network none` (no internet access)
- `--memory 128m` (memory cap)
- `--pids-limit 50` (process limit)
- Read-only filesystem + tmpfs
- 32 forbidden pattern checks before execution

---

## Why Open Source?

I believe the best learning tools should be free. Every student deserves to **see** how their code works, not just memorize rules about it.

If you're a CS student struggling with pointers, closures, or the event loop — give it a try. If you're a developer who wants to contribute, PRs are welcome.

---

## Links

- **Live Demo**: [codeinsight.online](https://codeinsight.online)
- **GitHub**: [github.com/jammy0903/CodeInsight](https://github.com/jammy0903/CodeInsight) (MIT License)

I'd love your feedback — what concepts should I visualize next? What languages should I add? Drop a comment or open an issue on GitHub.

---

*Built by a solo developer who just wanted to understand `int *p = &x;`.*
