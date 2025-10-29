"""
Ask Ahmed - AI Chat Assistant for CALIDUS Requirements Management System
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
import anthropic
import json

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.requirement import Requirement
from app.models.test_case import TestCase
from app.models.traceability import TraceabilityLink
from app.config import get_settings

router = APIRouter()
settings = get_settings()


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context_type: Optional[str] = "auto"  # auto, requirements, tests, traceability


async def get_system_context(db: Session, context_type: str = "auto") -> str:
    """Generate system context based on database content with REAL-TIME test execution data"""

    # Get counts and stats
    total_requirements = db.query(Requirement).count()
    total_tests = db.query(TestCase).count()
    total_links = db.query(TraceabilityLink).count()

    # Get requirement type breakdown
    req_by_type = {}
    for req_type in ["Aircraft_High_Level_Requirement", "System_Requirement", "Technical_Specification", "Certification_Requirement"]:
        count = db.query(Requirement).filter(Requirement.type == req_type).count()
        req_by_type[req_type] = count

    # Get status breakdown
    req_by_status = {}
    for status_val in ["draft", "approved", "under_review", "deprecated"]:
        count = db.query(Requirement).filter(Requirement.status == status_val).count()
        req_by_status[status_val] = count

    # Get priority breakdown
    req_by_priority = {}
    for priority in ["Critical", "High", "Medium", "Low"]:
        count = db.query(Requirement).filter(Requirement.priority == priority).count()
        req_by_priority[priority] = count

    # ============================================================================
    # REAL-TIME TEST EXECUTION DATA
    # ============================================================================

    # Get test execution status breakdown
    test_by_status = db.query(
        TestCase.status,
        func.count(TestCase.id)
    ).group_by(TestCase.status).all()
    test_status_dict = {status: count for status, count in test_by_status}

    # Get test type breakdown
    test_by_type = db.query(
        TestCase.test_type,
        func.count(TestCase.id)
    ).filter(TestCase.test_type.isnot(None)).group_by(TestCase.test_type).all()

    # Get automation breakdown
    automated_count = db.query(TestCase).filter(TestCase.automated == True).count()
    manual_count = db.query(TestCase).filter(TestCase.automated == False).count()

    # Calculate test execution metrics
    passed_count = test_status_dict.get("passed", 0)
    failed_count = test_status_dict.get("failed", 0)
    pending_count = test_status_dict.get("pending", 0)
    blocked_count = test_status_dict.get("blocked", 0)
    in_progress_count = test_status_dict.get("in_progress", 0)

    if total_tests > 0:
        pass_rate = (passed_count / total_tests) * 100
        executed_count = passed_count + failed_count
        execution_coverage = (executed_count / total_tests) * 100
    else:
        pass_rate = 0
        execution_coverage = 0

    # Get recent test executions (last 10)
    recent_tests = db.query(TestCase).filter(
        TestCase.execution_date.isnot(None)
    ).order_by(TestCase.execution_date.desc()).limit(10).all()

    # Get failed tests requiring attention
    failed_tests = db.query(TestCase).filter(
        TestCase.status == "failed"
    ).order_by(TestCase.execution_date.desc()).limit(10).all()

    # Get blocked tests
    blocked_tests = db.query(TestCase).filter(
        TestCase.status == "blocked"
    ).order_by(TestCase.updated_at.desc()).limit(10).all()

    context = f"""
# CALIDUS Requirements Management System Context

You are Ahmed, an AI assistant for the CALIDUS Aerospace Requirements Management System. You have comprehensive knowledge of all aerospace requirements, regulations, test cases, and traceability relationships in the system.

## System Overview
- **Total Requirements**: {total_requirements:,}
- **Total Test Cases**: {total_tests:,}
- **Total Traceability Links**: {total_links:,}

## Requirements Breakdown

### By Type:
- AHLR (Aircraft High Level): {req_by_type.get('Aircraft_High_Level_Requirement', 0):,}
- System Requirements: {req_by_type.get('System_Requirement', 0):,}
- Technical Specifications: {req_by_type.get('Technical_Specification', 0):,}
- Certification Requirements: {req_by_type.get('Certification_Requirement', 0):,}

### By Status:
- Draft: {req_by_status.get('draft', 0):,}
- Approved: {req_by_status.get('approved', 0):,}
- Under Review: {req_by_status.get('under_review', 0):,}
- Deprecated: {req_by_status.get('deprecated', 0):,}

### By Priority:
- Critical: {req_by_priority.get('Critical', 0):,}
- High: {req_by_priority.get('High', 0):,}
- Medium: {req_by_priority.get('Medium', 0):,}
- Low: {req_by_priority.get('Low', 0):,}

## Real-Time Test Execution Data

### Test Execution Status:
- **Passed**: {passed_count:,} tests
- **Failed**: {failed_count:,} tests  🚨
- **Pending**: {pending_count:,} tests
- **Blocked**: {blocked_count:,} tests  ⚠️
- **In Progress**: {in_progress_count:,} tests

### Test Execution Metrics:
- **Pass Rate**: {pass_rate:.1f}% ({passed_count:,} of {total_tests:,} tests passed)
- **Execution Coverage**: {execution_coverage:.1f}% ({passed_count + failed_count:,} tests executed)
- **Tests Requiring Action**: {failed_count + blocked_count:,} tests (failed + blocked)

### Test Automation:
- **Automated Tests**: {automated_count:,}
- **Manual Tests**: {manual_count:,}

### Test Types Distribution:
"""

    for test_type, count in test_by_type:
        context += f"- {test_type}: {count:,}\n"

    context += "\n### Recent Test Executions (Last 10):\n"
    if recent_tests:
        for test in recent_tests:
            exec_date = test.execution_date.strftime("%Y-%m-%d %H:%M") if test.execution_date else "N/A"
            duration = f"{test.execution_duration}s" if test.execution_duration else "N/A"
            executor = test.executed_by or "N/A"
            context += f"- **{test.test_case_id}**: {test.title[:60]}... | Status: {test.status} | Date: {exec_date} | Duration: {duration} | By: {executor}\n"
    else:
        context += "- No recent test executions found\n"

    context += "\n### Failed Tests Requiring Attention:\n"
    if failed_tests:
        for test in failed_tests:
            req_id = test.requirement.requirement_id if test.requirement else "N/A"
            context += f"- **{test.test_case_id}**: {test.title[:60]}... | Requirement: {req_id} | Type: {test.test_type or 'N/A'}\n"
    else:
        context += "- ✅ No failed tests currently\n"

    context += "\n### Blocked Tests:\n"
    if blocked_tests:
        for test in blocked_tests:
            req_id = test.requirement.requirement_id if test.requirement else "N/A"
            context += f"- **{test.test_case_id}**: {test.title[:60]}... | Requirement: {req_id} | Type: {test.test_type or 'N/A'}\n"
    else:
        context += "- ✅ No blocked tests currently\n"

    context += """

## Your Capabilities:
1. **Direct Database Access**: You have tools to query ANY test case or requirement in the system by ID
   - Use get_test_case_by_id() to retrieve complete details about any test case (e.g., TC-000942)
   - Use get_requirement_by_id() to retrieve complete details about any requirement (e.g., SYS-00018)
   - Use search_test_cases() to find test cases by keyword
   - Use search_requirements() to find requirements by keyword

2. **Test Execution Analysis**: Analyze test results, pass rates, failed tests, and execution trends (REAL-TIME DATA)

3. **Analysis**: Analyze compliance, coverage, risks, and gaps in the requirements

4. **Reporting**: Generate summaries, statistics, and reports with current test execution data

5. **Guidance**: Provide aerospace regulatory guidance (FAA, EASA, UAE GCAA)

6. **Recommendations**: Suggest improvements, missing links, or potential issues based on test results

IMPORTANT: When a user asks about a specific test case ID or requirement ID, ALWAYS use the appropriate tool to look it up in the database. Never say you don't have information about a specific ID - use the tools to retrieve it!

## Regulatory Context:
The system manages compliance across multiple aerospace regulations including:
- **USA (FAA)**: 14 CFR Parts 21, 23, 25, 33, DO-178C
- **EU (EASA)**: CS-23, CS-25, Part-21
- **UAE (GCAA)**: UAEMAR-21, UAEMAR-M
- **International**: ICAO Annexes, NATO STANAGs

## Response Guidelines:
- Be precise and professional
- Cite specific requirement IDs and test case IDs when relevant
- Use aerospace terminology appropriately
- Provide actionable insights, especially for failed or blocked tests
- When discussing tests, use the REAL-TIME execution data provided above
- Alert users to failed tests and blocked tests that require immediate attention
- Calculate and present metrics like pass rates and execution coverage

## CRITICAL FORMATTING RULES:
- DO NOT use Markdown formatting symbols (##, ###, **, *, _, etc.)
- DO NOT use hashtags for headings
- DO NOT use asterisks for bold or emphasis
- Write in PLAIN TEXT with natural conversational formatting
- Use simple line breaks and indentation for structure
- Use emojis sparingly and naturally (✅, 🚨, ⚠️, 📊)
- Format like you're writing an email or chat message, not a Markdown document
- Use uppercase for emphasis instead of bold (e.g., "CRITICAL" not "**CRITICAL**")
- Use dashes or numbers for lists without any special symbols

When users ask questions, you can:
- Search for requirements by ID, type, status, or content
- Analyze real-time test execution data, identify failed tests, and suggest corrective actions
- Analyze traceability and coverage
- Generate reports and statistics with current test execution metrics
- Provide regulatory guidance
- Identify gaps, risks, and tests requiring attention
"""

    return context


def get_test_case_by_id(db: Session, test_case_id: str) -> dict:
    """Query database for a specific test case by its ID"""
    test_case = db.query(TestCase).filter(TestCase.test_case_id == test_case_id).first()

    if not test_case:
        return {"error": f"Test case {test_case_id} not found"}

    # Get requirement details if linked
    requirement = test_case.requirement

    return {
        "test_case_id": test_case.test_case_id,
        "title": test_case.title,
        "description": test_case.description,
        "status": test_case.status,
        "priority": test_case.priority,
        "test_type": test_case.test_type,
        "test_steps": test_case.test_steps,
        "expected_results": test_case.expected_results,
        "actual_results": test_case.actual_results,
        "preconditions": test_case.preconditions,
        "automated": test_case.automated,
        "automation_script": test_case.automation_script,
        "test_environment": test_case.test_environment,
        "execution_date": test_case.execution_date.isoformat() if test_case.execution_date else None,
        "execution_duration": test_case.execution_duration,
        "executed_by": test_case.executed_by,
        "requirement_id": requirement.requirement_id if requirement else None,
        "requirement_title": requirement.title if requirement else None,
        "created_at": test_case.created_at.isoformat() if test_case.created_at else None,
        "updated_at": test_case.updated_at.isoformat() if test_case.updated_at else None
    }


def get_requirement_by_id(db: Session, requirement_id: str) -> dict:
    """Query database for a specific requirement by its ID"""
    requirement = db.query(Requirement).filter(Requirement.requirement_id == requirement_id).first()

    if not requirement:
        return {"error": f"Requirement {requirement_id} not found"}

    # Get linked test cases
    test_cases = requirement.test_cases

    # Get traceability links
    parent_links = db.query(TraceabilityLink).filter(TraceabilityLink.target_id == requirement.id).all()
    child_links = db.query(TraceabilityLink).filter(TraceabilityLink.source_id == requirement.id).all()

    return {
        "requirement_id": requirement.requirement_id,
        "title": requirement.title,
        "description": requirement.description,
        "type": requirement.type,
        "status": requirement.status,
        "priority": requirement.priority,
        "category": requirement.category,
        "verification_method": requirement.verification_method,
        "regulatory_document": requirement.regulatory_document,
        "regulatory_section": requirement.regulatory_section,
        "version": requirement.version,
        "test_cases": [{"id": tc.test_case_id, "title": tc.title, "status": tc.status} for tc in test_cases],
        "test_case_count": len(test_cases),
        "parent_requirements": [db.query(Requirement).get(link.source_id).requirement_id for link in parent_links if db.query(Requirement).get(link.source_id)],
        "child_requirements": [db.query(Requirement).get(link.target_id).requirement_id for link in child_links if db.query(Requirement).get(link.target_id)],
        "created_at": requirement.created_at.isoformat() if requirement.created_at else None,
        "updated_at": requirement.updated_at.isoformat() if requirement.updated_at else None
    }


def search_test_cases(db: Session, query: str, limit: int = 10) -> list:
    """Search for test cases by title or description"""
    test_cases = db.query(TestCase).filter(
        (TestCase.title.ilike(f"%{query}%")) |
        (TestCase.description.ilike(f"%{query}%")) |
        (TestCase.test_case_id.ilike(f"%{query}%"))
    ).limit(limit).all()

    return [
        {
            "test_case_id": tc.test_case_id,
            "title": tc.title,
            "status": tc.status,
            "priority": tc.priority,
            "test_type": tc.test_type,
            "requirement_id": tc.requirement.requirement_id if tc.requirement else None
        }
        for tc in test_cases
    ]


def search_requirements(db: Session, query: str, limit: int = 10) -> list:
    """Search for requirements by title or description"""
    requirements = db.query(Requirement).filter(
        (Requirement.title.ilike(f"%{query}%")) |
        (Requirement.description.ilike(f"%{query}%")) |
        (Requirement.requirement_id.ilike(f"%{query}%"))
    ).limit(limit).all()

    return [
        {
            "requirement_id": req.requirement_id,
            "title": req.title,
            "type": req.type,
            "status": req.status,
            "priority": req.priority,
            "category": req.category
        }
        for req in requirements
    ]


# Define tools for Claude to use
TOOLS = [
    {
        "name": "get_test_case_by_id",
        "description": "Get detailed information about a specific test case by its ID (e.g., TC-000942). Returns all test case details including status, steps, results, execution data, and linked requirement.",
        "input_schema": {
            "type": "object",
            "properties": {
                "test_case_id": {
                    "type": "string",
                    "description": "The test case ID (e.g., TC-000942, TC-000001)"
                }
            },
            "required": ["test_case_id"]
        }
    },
    {
        "name": "get_requirement_by_id",
        "description": "Get detailed information about a specific requirement by its ID (e.g., SYS-00018, AHLR-001). Returns all requirement details including linked test cases, parent/child relationships, and regulatory information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "requirement_id": {
                    "type": "string",
                    "description": "The requirement ID (e.g., SYS-00018, AHLR-001)"
                }
            },
            "required": ["requirement_id"]
        }
    },
    {
        "name": "search_test_cases",
        "description": "Search for test cases by keyword in title, description, or ID. Returns a list of matching test cases with basic information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'flight control', 'communication')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_requirements",
        "description": "Search for requirements by keyword in title, description, or ID. Returns a list of matching requirements with basic information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'flight control', 'communication')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    }
]


async def stream_chat_response(messages: List[ChatMessage], system_context: str, db: Session):
    """Stream chat responses from Claude with tool support"""

    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Anthropic API key not configured"
        )

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Convert messages to Anthropic format
    anthropic_messages = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]

    try:
        # First request to Claude with tools
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=system_context,
            messages=anthropic_messages,
            tools=TOOLS
        )

        # Process tool calls if any
        while response.stop_reason == "tool_use":
            # Execute tools
            tool_results = []
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input

                    # Execute the tool
                    if tool_name == "get_test_case_by_id":
                        result = get_test_case_by_id(db, tool_input["test_case_id"])
                    elif tool_name == "get_requirement_by_id":
                        result = get_requirement_by_id(db, tool_input["requirement_id"])
                    elif tool_name == "search_test_cases":
                        result = search_test_cases(db, tool_input["query"], tool_input.get("limit", 10))
                    elif tool_name == "search_requirements":
                        result = search_requirements(db, tool_input["query"], tool_input.get("limit", 10))
                    else:
                        result = {"error": f"Unknown tool: {tool_name}"}

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": json.dumps(result)
                    })

            # Continue conversation with tool results
            anthropic_messages.append({"role": "assistant", "content": response.content})
            anthropic_messages.append({"role": "user", "content": tool_results})

            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=system_context,
                messages=anthropic_messages,
                tools=TOOLS
            )

        # Stream the final response
        for content_block in response.content:
            if hasattr(content_block, "text"):
                # Split text into chunks for streaming effect
                text = content_block.text
                chunk_size = 10
                for i in range(0, len(text), chunk_size):
                    chunk = text[i:i+chunk_size]
                    yield f"data: {json.dumps({'type': 'content', 'text': chunk})}\n\n"

        # Send completion signal
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except anthropic.APIError as e:
        error_message = f"Anthropic API error: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'message': error_message})}\n\n"
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'message': error_message})}\n\n"


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with Ahmed - AI assistant for requirements management

    Ahmed can now query the database directly to answer questions about:
    - Specific test cases by ID (e.g., TC-000942)
    - Specific requirements by ID (e.g., SYS-00018)
    - Search for test cases and requirements by keyword

    Returns a streaming response with Server-Sent Events
    """

    # Generate system context
    system_context = await get_system_context(db, request.context_type)

    # Return streaming response with database access
    return StreamingResponse(
        stream_chat_response(request.messages, system_context, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get("/chat/stats")
async def chat_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get system statistics for Ask Ahmed context
    """

    return {
        "total_requirements": db.query(Requirement).count(),
        "total_test_cases": db.query(TestCase).count(),
        "total_traceability_links": db.query(TraceabilityLink).count(),
        "api_status": "configured" if settings.anthropic_api_key else "not_configured"
    }
