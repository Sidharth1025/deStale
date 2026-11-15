# 🛡️ StaleGuard: Hackathon Demo Pitch & Script (3–5 Minutes)

> **Speaker Tone:** Confident, energetic, technically grounded, and focused on solving a real AI pain point.
> **Target Audience:** Hackathon Judges, Engineers, Product Managers.

---

## ⏱️ Minute 0:00 – 0:45 | The Hook & Problem Statement
*(Show Slide 1 & 2 / Open StaleGuard Dark Theme Dashboard)*

**Speaker:**
> "Judges, have you ever asked an AI model for the latest pricing of an API, the current CEO of a company, or the recommended version of a software framework, only to get an answer that was confidently completely wrong?
>
> We all have. The reason is the **Knowledge Cutoff Dilemma**. Large Language Models are frozen in time the day their pre-training dataset is finalized. World events move in seconds, but retraining foundation models takes months and millions of dollars.
>
> When an AI model quotes outdated pricing, deprecated code, or obsolete rules, companies lose money and users lose trust.
>
> That is why we built **StaleGuard** — the live stale-answer and hallucination detector for generative AI applications."

---

## ⏱️ Minute 0:45 – 1:45 | Architecture & Technology Stack
*(Point to the Sidebar and System Architecture Tab)*

**Speaker:**
> "Under the hood, StaleGuard doesn't just do a simple keyword search. It runs an autonomous 5-stage verification pipeline:
>
> 1. **Claim Extraction:** When an AI answer is pasted, StaleGuard routes it through **Bifrost**, MaximHQ's high-speed AI Gateway, which strips away conversational fluff and decomposes the answer into atomic, testable propositions.
> 2. **Live Internet Grounding:** Each factual claim is searched across the live web using the **Tavily Search API**, gathering snippets, canonical URLs, and publication dates.
> 3. **Multi-Source Synthesis:** Bifrost synthesizes the live evidence, evaluating whether the claim is *Verified*, *Outdated*, *Contradicted*, or *Uncertain*.
> 4. **Evidence-Based Freshness Scoring:** We calculate a 0 to 100 Freshness Index. Time-sensitive claims carry a 1.5x weight penalty, and our strict guardrail prevents any fact from being verified on a single blog's word.
> 5. **Automated Corrections:** If an answer is stale, StaleGuard extracts the modern ground truth so the user has the right information immediately."

---

## ⏱️ Minute 1:45 – 3:30 | Live Interactive Demonstration
*(Switch to the Fact-Check Engine Tab in Streamlit)*

**Speaker:**
> "Let's see StaleGuard in action right now!
>
> **Demo 1: The Outdated Pricing Trap**
> Let's look at this real-world AI answer:
> *'OpenAI's flagship model GPT-4 costs $30.00 per 1M input tokens. Claude 2 is Anthropic's flagship with 100k context. Llama 2 is the latest open-weights model.'*
>
> We click **Analyze Freshness**.
>
> Watch the pipeline work in real time:
> - Step 1: Bifrost extracts 3 distinct claims.
> - Step 2: Tavily queries live developer pricing from `openai.com` and `anthropic.com`.
> - Step 3: The Freshness Engine flags this answer with an **Overall Score of 13 / 100 — High Stale Risk**!
>
> Look at the badges:
> - Claim 1 is marked **Outdated (Score: 10/100)**. StaleGuard displays the modern truth: *'GPT-4o costs $2.50/1M tokens, a 92% price drop.'*
> - Claim 2 is marked **Outdated**. StaleGuard correctly notes that Claude 3.5 Sonnet superseded Claude 2 with a 200k context.
>
> Notice that every single claim provides an expandable drawer with clickable, authoritative source URLs, snippets, and publication dates.
>
> **Demo 2: Side-by-Side Diff & Compliance Export**
> Now look at the **Stale vs Fresh Diff** tab: it gives engineering teams an instant tabular diff of what was stale and what the current fact is.
>
> And for enterprise compliance, we can click **Download PDF Audit Report** — generating an official ReportLab PDF with complete audit timestamps and source citations."

---

## ⏱️ Minute 3:30 – 4:30 | Business Impact & Scalability
*(Show Slide 9 & 10)*

**Speaker:**
> "Why does this matter?
> - **Enterprise RAG & Copilots:** StaleGuard acts as a zero-trust guardrail before AI responses are displayed to end users.
> - **Efficiency:** By leveraging Bifrost's routing and Tavily's deduplication cache, we reduce redundant LLM calls and save up to 60% in token costs.
> - **Modularity:** It is built with clean Python 3.11, Pydantic schemas, and 100% automated test coverage.
>
> In conclusion, StaleGuard ensures that no AI application operates on yesterday's assumptions.
>
> Thank you, and we are ready for your questions!"
