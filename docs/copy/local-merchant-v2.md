# Local merchant sequence (v2)

**Who:** owner-operated restaurants, cafes, auto shops, salons, dry
cleaners. Usually the owner reads email on a phone between customers.
**Goal:** get one processing statement. The statement review is the meeting.
**Config:** [`config/sequences/local-merchant-v2.json`](../../config/sequences/local-merchant-v2.json)

## Day 0, variant A: the statement offer

> Subject: Golden Hour Bakery card fees
>
> Hi Lena,
>
> Saw Golden Hour Bakery just got registered with the state. Congrats on making it official.
>
> Most owners I talk to are paying a markup they never agreed to, buried in the statement. If you send me one recent statement, I'll show you line by line what you're paying and what it should be. No pitch until you've seen the math.
>
> Worth a look?
>
> Joaquin

| Line | Why it's there |
|---|---|
| Subject with their business name | Looks like it's about them, because it is. Linted to 45 chars with the longest name we could find. |
| Signal opener | Proves this isn't a blast. Swapped per signal: permit, filing, ownership change, review spike, hiring, fee complaint. |
| "a markup they never agreed to" | Owners don't feel "high rates". They feel "something on this statement doesn't add up". |
| "line by line" | Concrete. They can picture what they'll get. |
| "No pitch until you've seen the math" | Removes the main reason not to reply. |
| "Worth a look?" | Single, low-effort ask. Yes is one word. |

## Day 0, variant B: the effective-rate question

> Subject: quick question, Dave
>
> Hi Dave,
>
> Saw your post about card fees eating into margin. That one comes up a lot with auto shop owners in San Pedro.
>
> Do you know your effective rate, all fees in, divided by what you processed last month? Most owners guess low by about a point. I can work it out from one statement and send it back the same day.
>
> Joaquin

**Hypothesis being tested:** a question that makes them realize they
*don't know* their number (B) pulls more replies than a direct offer (A).

**What I expect could go wrong with B:** it's a quiz. Some owners will
feel tested, not helped. That's why the test measures positive replies,
not total replies.

**Current read (synthetic sample data):** A 0.95% positive vs B 0.25%,
z = 1.31. A is ahead but not proven. Keep both running.

## Day 3: lower the effort further

> Subject: one photo is enough
>
> Dave, the fastest version: snap a photo of page one of your statement and reply here. I'll send back your effective rate and where the extra is coming from.

The day 0 ask was "send a statement". Day 3 makes it smaller: one photo,
one page. No new pitch.

*v1 used "re: {{business_name}} card fees" here. Dropped it: a fake "re:"
on a message that isn't a reply is a cheap trick, and the lint check
flagged it at 49 characters with long names anyway.*

## Day 7: call

Reference the email, ask who handles the statement, offer the review.
Voicemail is one sentence and a callback number. For tier A accounts with
an address, the walk-in task fires on day 2 and usually lands before this.

## Day 12: breakup

> Dave, I'll stop here. If fees ever come up, reply with a statement and I'll run the numbers. Good luck with Harbor Brake and Tire.

No guilt, no "did I lose you?". Leaves the door open with the same
small ask. A "not now" that comes back three months later started here.

## What v2 changed from v1

| v1 | v2 | Why |
|---|---|---|
| Generic opener for everyone | Opener chosen from the account's strongest signal | Relevance was the biggest lever |
| "Can I get 15 minutes?" | "Send me one statement" | A shop owner won't book a meeting with a stranger. They will send a photo. |
| Link to a savings calculator | No links | Placement, and owners don't click links from strangers |
| Fake "re:" follow-up subject | Plain subject | Honest, and passed lint |
