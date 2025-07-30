from fastloop import FastLoop, LoopContext
from fastloop.integrations.gmail import GmailIntegration, GmailReceivedEvent

app = FastLoop("email-tools")


@app.loop(
    "email-reader",
    integrations=[
        GmailIntegration(
            email_address="luke@beam.cloud", app_password="testpass", poll_interval=10
        )
    ],
)
async def test_email_bot(context: LoopContext):
    email: GmailReceivedEvent | None = await context.wait_for(
        GmailReceivedEvent, timeout=1
    )
    if email:
        pass
