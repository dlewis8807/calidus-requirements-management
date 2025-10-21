"""
API endpoints for intelligent test failure analysis and suggestions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.test_case import TestCase
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.reasoning_agent import ReasoningAgent
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/test-cases", tags=["test-suggestions"])


class AnalyzeRequest(BaseModel):
    """Request to analyze a test failure"""
    execution_log: str
    environment: Optional[str] = None


class FeedbackRequest(BaseModel):
    """Feedback on suggestion helpfulness"""
    helpful: bool
    comment: Optional[str] = None


@router.post("/{test_case_id}/analyze", summary="Analyze failed test case")
async def analyze_test_failure(
    test_case_id: int,
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a failed test case and provide intelligent suggestions

    This endpoint uses a rule-based reasoning engine to:
    - Classify the failure type
    - Identify likely root causes
    - Suggest specific remediation actions
    - Find similar historical failures

    No LLM required - pure deterministic analysis
    """
    # Get test case with requirement
    test_case = db.query(TestCase).options(
        joinedload(TestCase.requirement)
    ).filter(TestCase.id == test_case_id).first()

    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {test_case_id} not found"
        )

    # Run reasoning agent
    agent = ReasoningAgent()
    report = agent.analyze_failure(test_case, request.execution_log)

    return {
        "test_case_id": test_case_id,
        "test_case_name": test_case.test_case_id,
        "failure_type": report.failure_type,
        "root_causes": [
            {
                "cause": rc.cause,
                "likelihood": rc.likelihood,
                "evidence": rc.evidence,
                "affected_components": rc.affected_components,
                "regulatory_impact": rc.regulatory_impact
            }
            for rc in report.root_causes
        ],
        "suggestions": [
            {
                "priority": s.priority,
                "action": s.action,
                "details": s.details,
                "code_locations": s.code_locations,
                "verification_steps": s.verification_steps,
                "estimated_effort_hours": s.estimated_effort_hours
            }
            for s in report.suggestions
        ],
        "similar_failures": report.similar_failures,
        "confidence_score": report.confidence_score,
        "analysis_timestamp": "2025-10-21T12:00:00Z"
    }


@router.get("/{test_case_id}/suggestions", summary="Get test suggestions")
async def get_test_suggestions(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get existing suggestions for a test case

    Returns previously analyzed suggestions from the database
    """
    # Verify test case exists
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {test_case_id} not found"
        )

    # TODO: Query test_case_suggestions table when implemented
    return {
        "test_case_id": test_case_id,
        "suggestions": [],
        "message": "Suggestion history not yet implemented. Use /analyze endpoint for real-time analysis."
    }


@router.post("/suggestions/{suggestion_id}/feedback", summary="Submit suggestion feedback")
async def submit_suggestion_feedback(
    suggestion_id: int,
    feedback: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback on whether a suggestion was helpful

    This helps the system learn over time by tracking which suggestions
    engineers find useful vs not useful.
    """
    # TODO: Save feedback to suggestion_feedback table when implemented
    return {
        "suggestion_id": suggestion_id,
        "feedback_recorded": True,
        "helpful": feedback.helpful,
        "comment": feedback.comment,
        "user_id": current_user.id,
        "message": "Feedback functionality will be implemented with database tables"
    }


@router.get("/analysis-stats", summary="Get analysis statistics")
async def get_analysis_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about test failure analysis

    Returns metrics about:
    - Total analyses performed
    - Most common failure types
    - Average confidence scores
    - Most helpful suggestions
    """
    # TODO: Implement when suggestion history is tracked
    return {
        "total_analyses": 0,
        "analyses_this_week": 0,
        "average_confidence": 0.0,
        "most_common_failure_type": None,
        "message": "Statistics will be available when analysis history is tracked"
    }
