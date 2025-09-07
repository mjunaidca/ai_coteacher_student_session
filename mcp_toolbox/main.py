from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from typing import Any

# Simple test data
STUDENTS = {
    "mjunaid_ca": {
        "name": "Muhammad Junaid",
        "level": "beginner",
        "active_cursor_position": {
            "course_id": "AI-101",
            "topic_id": "00_prompt_engineering"
        }
    }
}

COURSES = {
    "AI-101": {
        "title": "Low Code n8n Agentic AI Development & Modern Python Programming",
        "toc": [
            {"name":"00_prompt_engineering", "description":"Introduction to Prompt Engineering"},
            {"name":"01_quick_start", "description":"Quick Start"},
            {"name":"02_beginner_tutorial", "description":"Beginner Tutorial"},
            {"name":"03_code_expressions", "description":"Code Expressions"},
            {"name":"04_ai_agents", "description":"AI Agents"},
            {"name":"05_mcp", "description":"MCP"},
        ]
    }
}

TOPICS = {
    "00_prompt_engineering": {
        "title": "Introduction to Prompt Engineering",
        "content": "Learn the basics of prompt engineering - how to write clear instructions for AI systems.",
        "topic_id": "00_prompt_engineering"
    }
}

mcp_app: FastMCP = FastMCP(name="STUDY_MODE_TOOLBOX", stateless_http=True,)

@mcp_app.tool(
    name="get_student_profile",
    description="Get basic student information for teaching"
)
def get_student_profile(user_id: str, auth_token: str) -> dict[str, Any]:
    if user_id in STUDENTS:
        return STUDENTS[user_id]
    raise ValueError(f"Student {user_id} not found")

@mcp_app.tool(
    name="get_course_basic_info", 
    description="Get basic course information"
)
def get_course_basic_info(course_id: str, auth_token: str) -> dict[str, Any]:
    if course_id in COURSES:
        return COURSES[course_id]
    raise ValueError(f"Course {course_id} not found")

@mcp_app.tool(
    name="get_table_of_contents",
    description="Get course modules list"
)
def get_table_of_contents(course_id: str, auth_token: str) -> dict[str, Any]:
    print(f"Getting table of contents for course {course_id}")
    if course_id in COURSES:
        toc = COURSES[course_id]["toc"]
        # Return a flat dictionary with each module as a key-value pair
        result = {"course_id": course_id, "total_modules": len(toc)}
        for i, module in enumerate(toc):
            result[f"module_{i}"] = f"{module['name']}: {module['description']}"
        return result
    raise ValueError(f"Course {course_id} not found")

@mcp_app.tool(
    name="get_personalized_content",
    description="Get content for a topic"
)
def get_personalized_content(topic_id: str, user_id: str, auth_token: str) -> dict[str, Any]:
    if topic_id in TOPICS:
        return TOPICS[topic_id]
    raise ValueError(f"Topic {topic_id} not found")

@mcp_app.tool(
    name="check_topic_completion",
    description="Check if student completed a topic"
)
def check_topic_completion(topic_id: str, user_id: str, auth_token: str) -> bool:
    if topic_id in TOPICS:
        return False  # Simple: nobody completed anything yet
    raise ValueError(f"Topic {topic_id} not found")

@mcp_app.tool(
    name="get_current_topic",
    description="Get student's current topic"
)
def get_current_topic(user_id: str, auth_token: str) -> dict[str, Any]:
    if user_id in STUDENTS:
        student = STUDENTS[user_id]
        return {
            "topic_id": student["active_cursor_position"]["topic_id"],
            "title": TOPICS.get(student["active_cursor_position"]["topic_id"], {}).get("title", "Unknown Topic")
        }
    # Default to prompt engineering - first topic of course
    return {"topic_id": "00_prompt_engineering", "title": "Introduction to Prompt Engineering"}

streamable_http_app: Starlette = mcp_app.streamable_http_app()

if __name__ == "__main__":
    port = 8001
    import uvicorn
    uvicorn.run("main:streamable_http_app", host="0.0.0.0", port=port, reload=True)