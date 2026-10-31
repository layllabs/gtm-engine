# Drafts awaiting approval

Every email below passed the lint gate. Call steps are scripts for the rep.

## Andora Travel Group (Miami)
`payments-orchestration-v1` variant B, opener from signal `multi_psp_detected`

**Day 0 email.** Subject: `one question on checkout`

> Hi Lucia,
>
> Noticed Andora Travel Group runs more than one payment provider at checkout.
>
> One question: when a transaction soft-declines today, does anything retry it on a second provider, or does the customer just see an error? If it's the second, that's usually a couple of points of authorization rate sitting on the table, and it's a config change rather than a rebuild.
>
> Joaquin

**Day 4 email.** Subject: `the routing diagram`

> Lucia, the fastest version: send me the list of providers and countries you process in, and I'll send back a one page routing diagram showing where retries and local methods would go. No call needed for that part.
>
> Joaquin

**Day 8 call.** Call script: ask who owns checkout and whether auth rate is a tracked metric. Offer the routing diagram. If engineering, ask about integration time per new PSP today.

**Day 14 email.** Subject: `closing the loop`

> Lucia, I'll leave it here. If auth rates or a new market come up, reply and I'll send the routing diagram over. Good luck with the quarter.
>
> Joaquin

## Kestrel Marketplace (Austin)
`payments-orchestration-v1` variant B, opener from signal `new_market_launch`

**Day 0 email.** Subject: `one question on checkout`

> Hi Daniel,
>
> Saw Kestrel Marketplace opened up in a new market recently.
>
> One question: when a transaction soft-declines today, does anything retry it on a second provider, or does the customer just see an error? If it's the second, that's usually a couple of points of authorization rate sitting on the table, and it's a config change rather than a rebuild.
>
> Joaquin

**Day 4 email.** Subject: `the routing diagram`

> Daniel, the fastest version: send me the list of providers and countries you process in, and I'll send back a one page routing diagram showing where retries and local methods would go. No call needed for that part.
>
> Joaquin

**Day 8 call.** Call script: ask who owns checkout and whether auth rate is a tracked metric. Offer the routing diagram. If engineering, ask about integration time per new PSP today.

**Day 14 email.** Subject: `closing the loop`

> Daniel, I'll leave it here. If auth rates or a new market come up, reply and I'll send the routing diagram over. Good luck with the quarter.
>
> Joaquin

## Nimbus Mobility (Denver)
`payments-orchestration-v1` variant A, opener from signal `checkout_conversion_post`

**Day 0 email.** Subject: `authorization rates`

> Hi Priya,
>
> Read what your team shared about checkout conversion at Nimbus Mobility.
>
> At that point the question is usually not which provider, it's who decides per transaction: which one gets the first try, what happens on a soft decline, and what the local method mix looks like in each country. Teams that fix that see a measurable authorization lift. I can show you what that routing logic looks like on your provider mix.
>
> Worth 25 minutes with whoever owns checkout?
>
> Joaquin

**Day 4 email.** Subject: `the routing diagram`

> Priya, the fastest version: send me the list of providers and countries you process in, and I'll send back a one page routing diagram showing where retries and local methods would go. No call needed for that part.
>
> Joaquin

**Day 8 call.** Call script: ask who owns checkout and whether auth rate is a tracked metric. Offer the routing diagram. If engineering, ask about integration time per new PSP today.

**Day 14 email.** Subject: `closing the loop`

> Priya, I'll leave it here. If auth rates or a new market come up, reply and I'll send the routing diagram over. Good luck with the quarter.
>
> Joaquin
