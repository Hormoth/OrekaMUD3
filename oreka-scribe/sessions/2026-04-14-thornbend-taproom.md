---
date: 2026-04-14
mode: log
arc_type: hero_journey (the false call)
participants: [hormoth]
threads_touched: [quiet_graft, player_origin, father_search]
characters_active: [tessaly, griff, michele]
---

## The Thornbend Taproom Scene

### Setup

Thornbend is a vineyard settlement half a day south of Spur Tower. Small, warm, agricultural. A place people retire to. Tessaly — the retired scholar — lives here and has the lodestone the player needs. But Tessaly is out in the vineyards and won't be back until evening.

The player has a few hours to kill. There's a taproom. The kind of place where Long Road caravans stop for a night, vineyard workers drink after harvest, and information moves slowly but sticks.

### What the Player Encounters

The player enters the taproom. Normal activity. Vineyard workers. A caravan that pulled in this morning. In the corner, two conversations happening at adjacent tables that the player overhears naturally — not through eavesdropping, just proximity.

**Table 1 — Two caravan drivers, mid-conversation:**

> "...Griff's been up and down the road three times this season asking the same questions. His daughter. Farborn girl, young, vanished four months back."
>
> "Everybody knows Griff. Hard man to say no to."
>
> "He's not asking anyone to say no. He's asking them to *remember*. And some of them are remembering too well and going quiet about it, which is making him quieter, which is making everyone nervous."
>
> "He put out word he'd pay for information. Good money. Said anyone heading toward the towers should keep their eyes open."

**Table 2 — A merchant and a weigh-station clerk, quieter:**

> "...someone asking at Dry Fork about Farborn. Not Griff — someone else. Woman named Michele, or that's what the station master said. Came through, asked about caravan manifests, people matching a description. Professional. Not grief — business."
>
> "Unstrung?"
>
> (Long pause. The clerk drinks.) "I didn't say that."
>
> "You didn't not say it."
>
> "I said someone named Michele asked about Farborn at Dry Fork. That's all I said. You want more, go to the weigh station yourself."

The player hears two names. **Griff** — a father looking for his daughter, offering to pay, the kind of search born from grief. **Michele** — someone else looking for the same girl, professional, maybe Unstrung. Two threads pointing at the same missing woman from opposite ends of the road.

Neither conversation is addressed to the player. Nobody asks them to do anything. The information is just *there*, sitting in a taproom, waiting for someone to pick it up.

### What This Triggers

**Arc checklist (hidden, automatic on room entry):**
- `visited_thornbend` → checked (place_visited)

**If the player asks the caravan drivers about Griff:**
- `heard_about_griff` → checked (fact_learned)
- The drivers say Griff is usually two days south at the Long Road junction. He'd talk to anyone with Spur Tower access.

**If the player asks about Michele:**
- `heard_about_michele` → checked (fact_learned)
- The clerk goes quiet. "I already said more than I should have. Ask at Dry Fork."

**If the player does neither and just waits for Tessaly:**
- Nothing triggers. The information was available. The player chose not to pick it up. Vaerix's arc still progresses through other channels — but slower.

### Why This Works

The player came to Thornbend for a lodestone. A fetch quest for a feat. They're killing time in a taproom because an NPC is out in the vineyards. And in the dead space of *waiting*, the real story brushes past them. Two names. One missing woman. The player didn't accept a quest. They overhead a conversation. What they do with it is entirely on them.

## Quest Hooks Identified

- **Follow Griff's thread**: travel to the Long Road junction, find Griff, hear his side. Leads to Act 1-2 patron relationship.
- **Follow Michele's thread**: travel to Dry Fork Station, find the weigh station, ask about Michele. Leads to Khadi and the Unstrung intelligence file.
- **Ignore both**: earn the feat, do the research, and let the story come to you through NPC `arc_reactions` and `rpsay` encounters. Slower but still works.
