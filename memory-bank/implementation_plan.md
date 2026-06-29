# Plan: Add Slash Command Chips to Chatbot Frontend

Me plan to add interactive suggestion chips above chat input box in chatbot page to guide user about slash commands like `/search` and `/interview`.

## User Review Required

> [!NOTE]
> Chips will appear above input box in both welcome screen and active chat screen. Click chip auto-fills prefix and focus input text.

## Proposed Changes

### Frontend Components

#### [MODIFY] [page.tsx](file:///d:/Job-Market-Analytics-Platform/frontend/ai%20assistant/page.tsx)
* Add command chips logic inside `ChatInput` component.
* Create list of chips:
  * `🔍 /search [role/city]` -> sets `/search `
  * `💬 /interview [role]` -> sets `/interview `
  * `📄 /review (CV review)` -> sets `/review`
  * `🤝 /match (Job match)` -> sets `/match `
* Use React `useRef` to focus `textarea` after chip click.
* Use Lucide icons: `Search`, `Sparkles`, `FileText`, `BarChart2`.
* Style chips with modern tailwind layout: flex wrap, rounded borders, micro-animations, glassmorphism-friendly colors.

## Verification Plan

### Manual Verification
* Run local dev server with `npm run dev`.
* Open chatbot page.
* Check that chips render above input on welcome screen.
* Click `/search` chip. Check input focus and value fill `/search `.
* Click `/interview` chip. Check input focus and value fill `/interview `.
* Send messages, check chips still render above input in active chat mode.
