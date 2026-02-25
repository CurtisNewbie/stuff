---
name: start
description: Start conversation
---

We are starting a conversation, below are the rules and requirements that you need to know.

# Things to start with:
1. Check AGENTS.md file, create it if not exists, write down important requirements from the user (including following requirements).

# Requirements:
1. ALWAYS use planning-with-files skill, unless the task can be completed in less than 3 steps.
2. Update AGENTS.md for importants things that must be remembered.
3. Once you have shown you plan to user, do not change to alternative solution unless user agree so, always confirm with the user. If the solution doesn't work, just say it, don't be "smart".
4. If you are completing programming tasks, always check if project compiles if you have modified the code.
5. For java project, always add `@author yongj.zhuang` if the class is newly created.

IMPORTANT: Do not put everything inside AGENTS.md. For design or implementation documentation, create a agentdoc/ folder and write your documents there instead; briefly describe the doc available to agents in AGENTS.md so they can look them up if needed. E.g., agentdoc/architect.md, agentdoc/design.md or agentdoc/faq.md.