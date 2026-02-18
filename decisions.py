low_stakes_email = """
Respond to the following email:
From: alice@example.com
Subject: Coffee?
Body: Hey, would you like to grab coffee next week?
"""

# Consequential email
consequential_email = """
Respond to the following email:
From: partner@startup.com
Subject: Budget proposal for Q1 2026
Body: Hey Sydney, we need your sign-off on the $1M engineering budget for Q1. Can you approve and reply by EOD? This is critical for our timeline.
"""

# Approval decision
approval = {
    "decisions": [
        {
            "type": "approve"
        }
    ]
}

# Edit decision
edit = {
    "decisions": [
        {
            "type": "edit",
            "edited_action": {
                "name": "send_email",
                "args": {
                    "recipient": "partner@startup.com",
                    "subject": "Budget proposal for Q1 2026",
                    "body": "I can only approve up to 500k, please send over details.",
                }
            }
        }
    ]
}

# Reject decision
reject = {
    "decisions": [
        {
            "type": "reject",
            "message": "Please edit the email asking for more details about the budget proposal, then send the email"
        }
    ]
}


list_of_decisions = {
    "decisions": [
        {
            "type": "approve"
        },
        {
            "type": "approve"
        },
        {
            "type": "approve"
        }
    ]
}