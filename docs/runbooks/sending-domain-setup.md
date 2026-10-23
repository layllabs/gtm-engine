# Runbook: stand up a cold-email sending domain

From registering the domain to the first cold send. Written for the person
doing it, in order, with the checks that catch the common mistakes. The
thresholds match `config/deliverability.json`.

## 0. Decide

- The primary brand domain never sends cold. Buy lookalikes.
- Two or three lookalike `.com` domains per sending identity. Not `.io`,
  not `.co` for SMB audiences; they look like spam to a shop owner.
- Two or three mailboxes per domain, mixed providers (one Google
  Workspace, one Microsoft 365) so a reputation problem at one provider
  does not take out the whole domain.
- Plan the daily cap before buying: 30 cold sends per mailbox per day
  after warmup. Six mailboxes is 180 sends a day. Size the list to that.

## 1. Register and park

- Register through a registrar with an API or at least bulk DNS editing.
- Set a redirect from each lookalike to the primary site. A lookalike that
  resolves to nothing looks like phishing to filters and to owners who
  check.
- Turn on WHOIS privacy.

## 2. DNS, in this order

For each lookalike domain:

1. **MX** records for the mailbox provider.
2. **SPF**: one TXT record at the root. One `v=spf1`, include only the
   providers that will actually send, end in `~all`. Two SPF records is a
   fail, and more than 10 DNS lookups is a fail.
3. **DKIM**: enable in the provider, publish the CNAME or TXT it gives you,
   wait for it to verify in the provider's admin before moving on.
4. **DMARC**: TXT at `_dmarc`. Start with `v=DMARC1; p=none; rua=mailto:...`
   so you get reports without blocking anything. Move to `p=quarantine`
   after two clean weeks.
5. **Custom tracking domain** if the sequencer uses link tracking (this
   engine sends no links on first touch, so this is optional).
6. **BIMI**: skip. Not worth it at this volume.

Check: send one message from each mailbox to a seed inbox you control and
read the headers. SPF pass, DKIM pass, DMARC pass. Do not proceed on any
fail.

## 3. Mailboxes

- Real display names. Real signature with a phone number. A profile photo.
  Filters and humans both check.
- Reply-to goes to a monitored inbox. Replies are the whole point.
- One person's name per mailbox. Do not rotate names on one address.

## 4. Warmup

- Enroll every mailbox in a warmup network on day one.
- Floor before any cold send: 14 days and 95% warmup reputation
  (`min_warmup_days`, `min_warmup_reputation`). Three weeks is better.
- During warmup the mailbox sends and replies to other warmup mailboxes
  only. No real prospects.
- Keep warmup running at a reduced rate after cold sending starts. It is
  the baseline that keeps reputation stable between campaigns.

## 5. First cold sends

- Ramp: 5 a day for three days, 10 for three days, 20 for three days,
  then 30. Watch bounce rate at each step.
- Verified addresses only. Catch-all and unknown go to call-first.
- One sequence per domain at first, so a copy problem is isolated to one
  domain's stats.

## 6. Daily checks (automated: `python -m gtm health`)

| metric | watch | pause mailbox |
|---|---|---|
| bounce rate, 7 day | 1.5% | 2.0% |
| spam complaint rate, 7 day | 0.05% | 0.10% |

Rates are not meaningful under 50 sends; the health check says so instead
of guessing.

## 7. Weekly checks

- Placement test per domain: send to a seed list across providers,
  record inbox vs spam vs missing.
- Reply rate per copy variant. A variant under the floor
  (`reply_rate_floor_per_variant`) gets rewritten, not tweaked.
- DMARC aggregate reports: anything sending as your domain that you do
  not recognize.

## 8. Retire

Two mailboxes paused on one domain within 30 days: retire the domain. Stop
sending, keep DNS and the redirect up for 90 days so it does not look
abandoned, then let it lapse. Register a replacement and start at step 1.
Do not try to rehabilitate a burned domain; a new one is cheaper than the
time.

## Mistakes I have made or seen

- Two SPF records after adding a second provider. Everything soft-failed
  for a week before anyone read a header.
- Starting cold sends at day 7 because warmup "looked fine."
- Rotating three different sender names on one mailbox to "test
  personas." Filters read that as spoofing.
- Judging a variant on total replies. Half of them were unsubscribes.
- Letting a retired domain's DNS lapse immediately, so the redirect died
  and old recipients hit a parking page.
