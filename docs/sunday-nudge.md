# A Sunday nudge

A weekly review only helps if it happens. Most assistants can now run a prompt on a schedule. Set one up for `review_day` (Sunday evening by default) with this prompt:

```
Robin: score next week with the Load Meter and tell me in one or two lines:
the total, the band, and how many free evenings I have. Then ask if I want
to start the weekly review. Do not send, delete or book anything.
```

Keep it to that one question. A long automatic report tends to go unread; the review itself is where the thinking happens.

## Where to set it up

| Assistant | Feature |
| --- | --- |
| Gemini app | Scheduled actions (weekly) |
| ChatGPT | Tasks (weekly) |
| Claude | Scheduled tasks, where your plan offers them |
| Claude Code | A cron job running `claude -p "<prompt above>"` with a budget cap |

Scheduled runs follow Robin's sixth safety rule: they may read and draft, never send, delete or book.

Names and availability of these features change often and differ per plan. If your assistant has no scheduler, a recurring `Start Weekly Review` task or calendar reminder does the same job.
