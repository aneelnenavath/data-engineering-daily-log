# Day 28 — Alerting on Pipeline Failure

## Objective
Day 27 proved that a failing dbt test correctly fails the orchestrating Airflow
task, not just the standalone dbt CLI run. But a failure nobody is told about is
only half a safeguard. Day 28 adds real failure alerting on top of the Day 27
pipeline, and — following the same discipline as every other day in this
project — proves the alert actually fires by checking a real inbox, not by
trusting that the callback is configured.

## Setup
[MailHog](https://github.com/mailhog/MailHog) was run as a disposable fake SMTP
server on the same `daylog-net` Docker network as Airflow: port 1025 accepts
SMTP connections, port 8025 exposes a web UI and a JSON API for checking what
actually arrived. The Airflow container was recreated with SMTP environment
variables pointing at it:
AIRFLOW__SMTP__SMTP_HOST=mailhog
AIRFLOW__SMTP__SMTP_PORT=1025
AIRFLOW__SMTP__SMTP_MAIL_FROM=airflow@dayloguser.local
AIRFLOW__SMTP__SMTP_STARTTLS=False
AIRFLOW__SMTP__SMTP_SSL=False

No authentication needed — MailHog accepts anything sent to it and just
captures it for inspection.

## The DAG
The Day 27 `dbt_build` task was reused unchanged, with one addition: an
`on_failure_callback` that emails an alert using Airflow's own
`airflow.utils.email.send_email`, the same mechanism a real production DAG
would use for a Slack/PagerDuty-integrated email alert:

```python
def alert_on_failure(context):
    ti = context["task_instance"]
    subject = f"[Airflow] {ti.dag_id}.{ti.task_id} failed"
    body = (
        f"<p>Task <b>{ti.task_id}</b> in DAG <b>{ti.dag_id}</b> failed.</p>"
        f"<p>Run ID: {context['run_id']}</p>"
        f"<p>Execution date: {context['logical_date']}</p>"
        f"<p>Log URL: {ti.log_url}</p>"
    )
    send_email(to="anil@example.com", subject=subject, html_content=body)
```

`on_failure_callback` only fires when the task itself fails — it's not a
generic hook, so proving it end-to-end means proving both directions: it fires
on failure, and it stays silent on success.

## Proof: three runs, checked against a real inbox
Rather than trust that the callback was wired up correctly, every run's result
was cross-checked against MailHog's own API (`curl http://localhost:8025/api/v2/messages`),
not just Airflow's reported task state.

| run | seed data | Airflow state | MailHog inbox total |
|---|---|---|---|
| 1 | clean | success | 0 |
| 2 | planted bad row (`unknown_status`) | failed | 1 |
| 3 | bad row removed | success | 1 (unchanged) |

Run 1 confirmed a healthy pipeline sends no alert at all. Run 2 planted the
same `accepted_values`-violating row used on Day 27, and MailHog captured a
genuine SMTP message — subject `[Airflow] day28_dbt_pipeline_with_alert.dbt_build failed`,
`From: airflow@dayloguser.local`, `To: anil@example.com` — real evidence of an
actual email being sent and received, not just a Python function executing
without error. Run 3 confirmed the fix restored success *and* that the inbox
count stayed at exactly 1, proving a clean run doesn't add noise on top of a
real incident.

## Key takeaway
A failure callback is easy to configure and easy to leave silently broken —
misconfigured SMTP settings, a wrong recipient, or a callback that raises its
own exception can all fail invisibly while the DAG still shows the correct
`failed` state. The only way to actually trust it is the same way every other
safeguard in this project was trusted: trigger the real failure condition and
check independent evidence that the safeguard did its job, rather than reading
configuration and assuming it works.
