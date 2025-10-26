from fastapi import APIRouter, Request, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone

from database import get_db
from models import Refinement, Project, Branch
from integrations.github_api import github_client

router = APIRouter()

"""
IMPORTANT: CodeRabbit Integration Clarification
===============================================

CodeRabbit works via GitHub App installation, NOT via webhooks to external systems.

How it ACTUALLY works:
1. Install CodeRabbit GitHub App on your repos
2. CodeRabbit automatically reviews PRs when created/updated
3. CodeRabbit posts review comments directly on GitHub PRs
4. CodeRabbit can block PRs via pre-merge checks (configured in .coderabbit.yaml)

This webhook endpoint is for GITHUB webhooks, not CodeRabbit webhooks.
We can use it to:
- Monitor PR status changes (opened, closed, merged)
- Track when CodeRabbit posts comments (by parsing comment bodies)
- Update our database based on PR lifecycle events

To integrate CodeRabbit:
1. Install at: https://github.com/apps/coderabbitai
2. Add .coderabbit.yaml to your repo (see deployment/coderabbit.yaml)
3. CodeRabbit will automatically review all future PRs
"""

@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle incoming GitHub webhook events and update PR-related refinement state.
    
    Processes "pull_request", "issue_comment", and "pull_request_review" events from GitHub. For pull_request events, updates the corresponding Refinement record (by PR URL) to reflect opened, closed+merged (completed), or closed-not-merged (failed) states and commits those changes to the database. For issue_comment and pull_request_review events, detects CodeRabbit-originated activity and logs a preview.
    
    Parameters:
        request (Request): The incoming FastAPI request containing the webhook JSON payload.
        x_github_event (Optional[str]): The GitHub event type from the `X-GitHub-Event` header (e.g., "pull_request", "issue_comment", "pull_request_review").
        x_hub_signature_256 (Optional[str]): The `X-Hub-Signature-256` header value when a webhook secret is configured (used for payload verification if implemented).
        db (Session): Database session (injected via dependency) used to query and update Refinement records.
    
    Returns:
        dict: A response object with keys:
            - "success": `True` if the webhook was processed without error.
            - "message": Short status message.
            - "event": The GitHub event type received.
    
    Raises:
        HTTPException: Raised with status 500 if processing fails.
    """
    try:
        payload = await request.json()
        event_type = x_github_event
        
        print(f"\n======================================================================")
        print(f"GitHub Webhook Received: {event_type}")
        print(f"======================================================================")
        
        if event_type == "pull_request":
            action = payload.get("action")  # opened, closed, reopened, synchronize
            pr_data = payload.get("pull_request", {})
            pr_url = pr_data.get("html_url")
            pr_state = pr_data.get("state")  # open, closed
            merged = pr_data.get("merged", False)
            
            print(f"Action: {action}")
            print(f"PR URL: {pr_url}")
            print(f"State: {pr_state}, Merged: {merged}")
            
            # Update refinement status in database
            if pr_url:
                refinement = db.query(Refinement).filter(Refinement.pr_url == pr_url).first()
                if refinement:
                    if action == "opened":
                        refinement.status = "processing"
                    elif action == "closed" and merged:
                        refinement.status = "completed"
                        refinement.completed_at = datetime.now(timezone.utc)
                    elif action == "closed" and not merged:
                        refinement.status = "failed"
                        refinement.error_message = "PR closed without merging"
                    
                    db.commit()
                    print(f"✓ Updated refinement #{refinement.id} status to: {refinement.status}")
        
        elif event_type == "issue_comment":
            # Track when CodeRabbit posts comments
            comment_body = payload.get("comment", {}).get("body", "")
            comment_user = payload.get("comment", {}).get("user", {}).get("login", "")
            
            if "coderabbit" in comment_user.lower():
                print(f"✓ CodeRabbit comment detected")
                print(f"  Preview: {comment_body[:200]}...")
                # You could parse the comment to extract review scores, suggestions, etc.
        
        elif event_type == "pull_request_review":
            # Track PR reviews (including CodeRabbit's)
            review_state = payload.get("review", {}).get("state")  # approved, changes_requested, commented
            review_body = payload.get("review", {}).get("body", "")
            reviewer = payload.get("review", {}).get("user", {}).get("login", "")
            
            print(f"Review by {reviewer}: {review_state}")
            if "coderabbit" in reviewer.lower():
                print(f"✓ CodeRabbit review: {review_state}")
        
        print(f"======================================================================\n")
        
        return {
            "success": True,
            "message": "Webhook processed",
            "event": event_type
        }
    
    except Exception as e:
        print(f"❌ Error processing GitHub webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhooks/setup-instructions")
async def webhook_setup_instructions():
    """
    Provide setup instructions for installing the CodeRabbit GitHub App and for configuring a GitHub webhook endpoint.
    
    The response includes two sections:
    - `coderabbit_setup`: steps and links for installing and configuring the CodeRabbit GitHub App.
    - `github_webhook_setup`: guidance and the webhook URL (constructed from the incoming request URL) for subscribing to Pull Request, Pull Request Review, and Issue Comment events.
    
    Returns:
        dict: A mapping with keys `coderabbit_setup` and `github_webhook_setup`. `coderabbit_setup` contains installation steps, app URL, and config file location. `github_webhook_setup` contains the webhook purpose, GitHub UI steps, the webhook URL derived from the request, recommended events to subscribe to, and secret configuration advice.
    """
    return {
        "coderabbit_setup": {
            "step_1": "Install CodeRabbit GitHub App",
            "url": "https://github.com/apps/coderabbitai",
            "step_2": "Add .coderabbit.yaml to repo root",
            "config_location": "deployment/coderabbit.yaml in OPS-X repo",
            "step_3": "CodeRabbit will automatically review all PRs",
            "note": "No webhook setup needed for CodeRabbit - it works via GitHub App"
        },
        "github_webhook_setup": {
            "purpose": "Track PR lifecycle events in OPS-X backend",
            "step_1": "Go to GitHub repo → Settings → Webhooks",
            "step_2": f"Add webhook URL: {request.url.scheme}://{request.url.netloc}/api/webhooks/github",
            "step_3": "Select events: Pull requests, Pull request reviews, Issue comments",
            "step_4": "Set secret: GITHUB_WEBHOOK_SECRET from .env",
            "note": "This is optional - only needed if you want to sync PR status with OPS-X database"
        }
    }