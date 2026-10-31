# Objections in payments, what they mean, what works

The objection library format from the onboarding plan, filled in for this
vertical. Each entry: what they say, what it usually means, the response
that has worked, the response that has not.

## SMB

**"I'm locked in a contract."**
Means: they know the ETF exists and assume it kills the math.
Works: run the ETF payback in the calculator and say the number. "The $495
fee is covered in six weeks at the difference we found." Then: "And the
contract auto-renews on March 31, so the window to not renew is February.
Want me to set a reminder?"
Does not work: "We'll buy out your contract." Owners have heard it and it
reads as a trick, which it often is.

**"My rates are fine."**
Means: they have not computed their effective rate; they remember the
rate they were quoted.
Works: "Probably. Can I check? It takes one statement and I'll tell you
either way, including if you should stay." Then do exactly that, and say
so when they are fine.
Does not work: arguing with a number they have not seen yet.

**"I have a guy."**
Means: relationship with a rep or the POS vendor; switching feels like
disloyalty or hassle.
Works: "Keep him. I'm not asking you to switch today. I'm asking to show
you your effective rate, which he should have shown you. If he has, great."
Does not work: anything negative about the guy.

**"I don't have time."**
Means: true.
Works: shrink the ask. A photo of page one. Reply to this email. Two
minutes while they log in to the portal.
Does not work: "It'll only take 15 minutes."

**"I don't want to change equipment."**
Means: they have been burned by a POS migration or they lease terminals.
Works: find out what they have before promising anything; most common
terminals and POS systems can be re-programmed. If they lease, the lease
is often the bigger problem than the rate; show the lease math.
Does not work: "We'll give you free equipment." Free equipment is how
they got the lease.

**"Send me something."**
Means: polite no, or a real request for the written review.
Works: send the one-page review from the calculator against their actual
statement, the same day, and nothing else. No deck.
Does not work: a brochure.

**"We're all set" / "Not interested" / "Remove me."**
Means: no. The classifier labels these and the sequence stops. Recycle
only on a new signal. Suppression on a remove request is permanent.

## Enterprise

**"We already have two providers; we route ourselves."**
Means: they built routing logic in-house and it is someone's problem.
Works: "Then you know the failover and retry logic better than most. How
much of it is maintained versus how much was written once? And who adds
the next provider?" The diagram offer still applies: show what their
in-house logic would look like as config.
Does not work: implying their engineers did it wrong.

**"Another vendor in the critical path."**
Means: legitimate. Engineering is right to ask.
Works: answer the incident question directly: what happens when the
orchestration layer is down, what the failover to direct integration
looks like, latency numbers, status page history. Offer to put their
engineer on a call with yours.
Does not work: "99.99%."

**"Our auth rates are fine."**
Means: they may not have the number, or they have it blended across
markets.
Works: "What are they in [the hardest market they sell in]? That's usually
where the gap is." Then the pilot: one market, measure before and after.
Does not work: quoting a vendor case study as if it were their number.

**"We'd need to involve procurement / security / legal."**
Means: a real buying process. Good news.
Works: ask who, get the security questionnaire started in parallel with
the pilot, map the stakeholders.
Does not work: trying to shortcut it.

**"Pricing?"**
Means: they want to know whether it eats the gain.
Works: be direct about the model (per-transaction, tiered by volume,
platform fee, whatever it is) and show it against the recovered revenue
math on their volume. If the math does not work, say so.
Does not work: "Let's get on a call to discuss."

## Adding to this file

One objection a week, from a real call, with what was said and what
happened. That is the rule from the onboarding plan and it applies to me.
