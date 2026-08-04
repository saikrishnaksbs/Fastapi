"""
BACKGROUND TASKS
================
This script demonstrates how to configure background tasks.
FastAPI lets you register a function to be run after returning a response.
This is useful for sending emails, processing files, or running heavy calculations without delaying the user.
"""

import time
from fastapi import BackgroundTasks, FastAPI

app = FastAPI(title="Background Tasks")

# A normal python function containing the task logic
def write_notification(email: str, message: str = ""):
    # Simulate a slow email sending operation
    time.sleep(5)
    
    with open("notifications_log.txt", mode="a") as log_file:
        log_file.write(f"Notification sent to {email}: {message}\n")
    print(f"[BACKGROUND] Finished sending email to {email}")

@app.post("/send-notification/{email}")
def send_notification(
    email: str, 
    background_tasks: BackgroundTasks, 
    message: str = "Welcome to FastAPI!"
):
    # Register the task function and pass arguments to it.
    # FastAPI will respond immediately to the client and run the task in the background.
    background_tasks.add_task(write_notification, email, message=message)
    
    return {"message": "Notification scheduled in the background!"}

# To run this file:
# uvicorn 09_background_tasks_and_events.01_background_tasks:app --reload
