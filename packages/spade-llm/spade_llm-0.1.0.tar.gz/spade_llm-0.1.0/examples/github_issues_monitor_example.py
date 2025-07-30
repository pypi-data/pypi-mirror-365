"""
GitHub Issues/PRs Monitor with Email Notification System

Advanced 4-agent workflow demonstrating:
- Input guardrails (GitHub-only requests)
- GitHub MCP integration (list issues/PRs)
- Notion MCP with HTTP streaming (storage)
- Human-in-the-loop (email confirmation)
- Gmail MCP (email sending)

Agents:
- ChatAgent: Human interface with GitHub keyword guardrails
- GitHubAnalyzerAgent: GitHub MCP integration and analysis
- NotionManagerAgent: Notion MCP storage and forwarding
- EmailManagerAgent: HITL confirmation and Gmail sending

Workflow:
User request → ChatAgent (guardrails) → GitHubAnalyzerAgent (analysis) 
→ NotionManagerAgent (storage) → EmailManagerAgent (HITL + email)
"""

import asyncio
import getpass
import os
import re
import spade
import logging
from datetime import datetime
from typing import Dict, Any

from spade_llm.agent import LLMAgent, ChatAgent
from spade_llm.providers import LLMProvider
from spade_llm.mcp import StreamableHttpServerConfig, StdioServerConfig
from spade_llm.guardrails import KeywordGuardrail, GuardrailAction
from spade_llm.guardrails.base import Guardrail, GuardrailResult, GuardrailAction
from spade_llm.tools import HumanInTheLoopTool
from spade_llm.utils import load_env_vars

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



GITHUB_ANALYZER_PROMPT = """You are a GitHub analysis specialist. You receive GitHub monitoring requests and provide comprehensive repository analysis.

Your workflow:
1. Identify the repository to analyze (ask user if not specified)
2. Use GitHub MCP tools to gather data:
   - List recent issues (open and closed, last 30 days)
   - List recent pull requests (all states, last 30 days)
   - Get repository details if available
3. Analyze the collected data for patterns, priorities, and insights
4. Generate a structured summary with actionable information

IMPORTANT: 
- Always specify which repository you're analyzing
- Include actual numbers and real data from the GitHub API
- Focus on actionable insights and trends
- Identify urgent items that need attention

Response format:
=== GITHUB REPOSITORY ANALYSIS ===

🏪 Repository: [owner/repo-name]
📅 Analysis Date: [current date and time]
🔍 Analysis Period: Last 30 days

📊 SUMMARY METRICS
- Issues: [X] total ([X] open, [X] closed)
- Pull Requests: [X] total ([X] open, [X] merged, [X] draft, [X] closed)
- Recent Activity Level: [High/Medium/Low]
- Last Updated: [when]

🚨 URGENT ITEMS (High Priority)
[List critical issues/PRs that need immediate attention, include #numbers and titles]

📈 RECENT TRENDS (Last 30 days)
- New Issues Created: [X]
- Issues Closed: [X] 
- PRs Merged: [X]
- Most Active Contributors: [list top 3]
- Common Labels/Categories: [list most frequent]

🔍 KEY INSIGHTS
[Notable patterns, recurring issues, areas needing attention]

💡 RECOMMENDATIONS
[Actionable suggestions based on the analysis]

<GITHUB_SUMMARY>
{
  "repository": "[owner/repo]",
  "analysis_date": "[ISO date]",
  "period_days": 30,
  "summary": {
    "total_issues": X,
    "open_issues": X,
    "closed_issues": X,
    "total_prs": X,
    "open_prs": X,
    "merged_prs": X,
    "draft_prs": X
  },
  "urgent_items": [
    {"type": "issue/pr", "number": X, "title": "...", "priority": "high", "url": "..."}
  ],
  "trends": {
    "new_issues": X,
    "closed_issues": X,
    "merged_prs": X,
    "top_contributors": ["...", "..."],
    "common_labels": ["...", "..."]
  },
  "insights": ["...", "..."],
  "recommendations": ["...", "..."]
}
</GITHUB_SUMMARY>

This analysis will now be stored in Notion and potentially sent via email."""

NOTION_MANAGER_PROMPT = """You are a Notion storage specialist. You receive GitHub analysis summaries and store them systematically.

Your workflow:
1. Receive complete GitHub analysis from GitHubAnalyzer agent
2. Use Notion MCP tools to:
   - Search for "Spade monitoring" page
   - Add a new entry with all analysis data
   - Structure the data for easy reading


3. After successful storage, prepare the summary for email notification

IMPORTANT:
- Create consistent Notion entries for easy tracking over time
- Include the full analysis text for complete context
- Verify the data was stored before forwarding

Response format:
=== NOTION STORAGE COMPLETED ===

📚 **Notion Database Updated**
✅ Entry created: "[Repository] Analysis - [Date]"
🗂️  Database: GitHub Repository Monitoring
📊 Data stored:
   - Repository: [owner/repo]
   - Analysis Date: [date]
   - Issues: [X] total ([X] open)
   - PRs: [X] total ([X] open)

🔗 Notion URL: [if available]

📧 **Forwarding to Email Manager**
The complete analysis is now ready for potential email notification.

[Include the FULL original analysis text here for the Email Manager]"""

EMAIL_MANAGER_PROMPT = """You are an email notification specialist with human-in-the-loop confirmation. You receive GitHub analysis summaries and handle email notifications with human oversight.

Your workflow:
1. Receive complete GitHub analysis from Notion Manager
2. Extract key information and prepare a concise summary for human review
3. Use ask_human_expert tool to get human confirmation and email details
4. If approved, format and send professional email via Gmail MCP.
 Remember to do the email readable to a human with presentation and ending . Well structured
5. ALWAYS end with termination marker after completing the process

HUMAN INTERACTION PROCESS:
1. Present a concise executive summary to the human
2. Ask: "Would you like to send this GitHub analysis via email?"
3. If YES: Ask "Please provide the recipient's email address(es)"
4. If NO: Acknowledge and end with termination marker
5. If email provided: Send formatted email, confirm delivery, and end with termination marker

EMAIL FORMAT (when sending):
Subject: "GitHub Repository Analysis - [Repository Name] - [Date]"

Email Content :
---
# GitHub Repository Analysis Report

**Repository:** [owner/repo-name]  
**Analysis Date:** [date]  
**Period Analyzed:** Last 30 days

## Executive Summary
- **Issues:** [X] total ([X] open, [X] closed)
- **Pull Requests:** [X] total ([X] open, [X] merged)
- **Activity Level:** [High/Medium/Low]
- **Urgent Items:** [X] items need attention

## Key Insights
[3-4 most important insights from analysis]

## Urgent Items Requiring Attention
[List critical issues/PRs with numbers and titles]

## Recommendations
[Top 3 actionable recommendations]

## Full Analysis
[Include complete detailed analysis from GitHubAnalyzer]

---
*This report was generated automatically and stored in Notion for tracking.*

INTERACTION EXAMPLE:
When you receive analysis, use ask_human_expert with message like:
"GitHub analysis ready for [repo-name]. Key findings: [X] open issues, [Y] urgent items. 
Activity level: [level]. Would you like me to email this summary to someone?"

TERMINATION:
- After sending email successfully: "Email sent successfully to [recipient]. <EMAIL_PROCESS_COMPLETE>"
- After human declines email: "GitHub analysis completed and stored in Notion. No email sent. <EMAIL_PROCESS_COMPLETE>"

IMPORTANT:
- Always summarize key points for human decision-making
- Wait for explicit human approval before sending emails
- Include repository name and key metrics in human interaction
- Use professional email formatting
- Confirm successful email delivery
- ALWAYS end with <EMAIL_PROCESS_COMPLETE> termination marker"""


class GitHubOnlyGuardrail(Guardrail):
    """Custom guardrail that only allows GitHub-related requests."""
    
    def __init__(self, name: str = "github_only_filter", enabled: bool = True):
        super().__init__(name, enabled, "I only help with GitHub-related requests. Please ask about issues, pull requests, or repository monitoring.")
        self.github_keywords = [
            "github", "issue", "issues", "pull request", "pr", "prs", 
            "repository", "repo", "commit", "branch", "merge", "review",
            "bug", "feature", "enhancement", "milestone", "project",
            "analyze", "monitor", "check", "status", "activity"
        ]
    
    async def check(self, content: str, context: Dict[str, Any]) -> GuardrailResult:
        """Check if content is GitHub-related."""
        content_lower = content.lower()
        
        # Check if any GitHub keyword is present
        if any(keyword in content_lower for keyword in self.github_keywords):
            return GuardrailResult(
                action=GuardrailAction.PASS,
                content=content,
                reason="GitHub-related request detected"
            )
        else:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                content=self.blocked_message,
                reason="Non-GitHub request blocked"
            )


def create_github_guardrails():
    """Create input guardrails that only allow GitHub-related requests."""
    return [GitHubOnlyGuardrail()]


async def main():
    print("🐙 === GitHub Issues/PRs Monitor with Email Notification === 🐙\n")
    
    # Load environment variables
    load_env_vars()
    
    # Get API keys
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        openai_key = input("Enter your OpenAI API key: ")
    
    # XMPP server configuration
    xmpp_server = input("Enter XMPP server domain: ")
    
    # Agent credentials
    agents_config = {
        "chat": (f"github_chat@{xmpp_server}", "GitHub Chat Interface"),
        "analyzer": (f"github_analyzer@{xmpp_server}", "GitHub Analyzer Agent"),
        "notion": (f"notion_manager@{xmpp_server}", "Notion Storage Agent"),
        "email": (f"email_manager@{xmpp_server}", "Email Manager Agent"),
        "human": (f"human_expert@{xmpp_server}", "Human Expert")
    }
    
    # Get passwords
    passwords = {}
    for role, (jid, label) in agents_config.items():
        passwords[role] = getpass.getpass(f"{label} password: ")
    
    # Create LLM provider
    provider = LLMProvider.create_openai(
        api_key=openai_key,
        model="gpt-4.1-2025-04-14",
        temperature=0.7
    )
    
    # MCP Server configurations
    print("\n🔧 Configuring MCP servers...")
    
    # GitHub MCP server (HTTP streaming)
    github_mcp = StreamableHttpServerConfig(
        name="GitHubMCP",
        url="https://mcp.composio.dev/composio/server/1d9fa71f-916e-4a6b-8bb6-e68ef758f255/mcp?include_composio_helper_actions=true",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "SPADE_LLM/1.0"
        },
        timeout=30.0,
        sse_read_timeout=300.0,
        terminate_on_close=True,
        cache_tools=True
    )
    
    # Notion MCP server (HTTP streaming)
    notion_mcp = StreamableHttpServerConfig(
        name="NotionMCP",
        url="https://mcp.composio.dev/composio/server/902f9f2b-01dc-4af4-82ba-8707c3b11fe2/mcp?include_composio_helper_actions=true",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "SPADE_LLM/1.0"
        },
        timeout=30.0,
        sse_read_timeout=300.0,
        terminate_on_close=True,
        cache_tools=True
    )
    
    # Gmail MCP server (HTTP streaming)
    gmail_mcp = StreamableHttpServerConfig(
        name="GmailMCP",
        url="https://mcp.composio.dev/composio/server/0a3005ff-2ff2-4dcd-a949-37a0bbb8a03e/mcp?include_composio_helper_actions=true",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "SPADE_LLM/1.0"
        },
        timeout=30.0,
        sse_read_timeout=300.0,
        terminate_on_close=True,
        cache_tools=True
    )
    
    # Create human-in-the-loop tool for email manager
    human_tool = HumanInTheLoopTool(
        human_expert_jid=agents_config["human"][0],
        timeout=300.0,  # 5 minutes
        name="ask_human_expert",
        description="Ask human expert for email sending confirmation and recipient details"
    )
    
    # Create guardrails
    input_guardrails = create_github_guardrails()
    
    # Create agents with structured message flow
    print("\n🤖 Creating agents...")
    
    # WORKFLOW: User → Chat → Analyzer → Notion → Email → Human Expert
    
    # 1. Chat Agent with Guardrails (Entry Point)
    # Filters GitHub-only requests and forwards to analyzer
    # Display callback for chat responses
    def display_response(message: str, sender: str):
        print(f"\n🤖 GitHub Monitor: {message}")
        print("-" * 50)
    user_chat = ChatAgent(
        jid=agents_config["chat"][0],
        password=passwords["chat"],
        target_agent_jid=agents_config["analyzer"][0],
        display_callback=display_response,
        verify_security=False
    )

    # 2. GitHub Analyzer Agent (Data Collection & Analysis)
    # Uses GitHub MCP to analyze repositories and create structured summaries
    analyzer_agent = LLMAgent(
        jid=agents_config["analyzer"][0],
        password=passwords["analyzer"],
        provider=provider,
        system_prompt=GITHUB_ANALYZER_PROMPT,
        input_guardrails=input_guardrails,
        mcp_servers=[github_mcp],
        reply_to=agents_config["notion"][0],  # → NotionManager
        verify_security=False
    )
    
    # 3. Notion Manager Agent (Storage & Forwarding)
    # Stores analysis in Notion database and forwards to email manager
    notion_agent = LLMAgent(
        jid=agents_config["notion"][0],
        password=passwords["notion"],
        provider=provider,
        system_prompt=NOTION_MANAGER_PROMPT,
        mcp_servers=[notion_mcp],
        reply_to=agents_config["email"][0],  # → EmailManager
        verify_security=False
    )
    
    # 4. Email Manager Agent (HITL & Email Sending)
    # Uses human-in-the-loop for email confirmation and Gmail MCP for sending
    email_agent = LLMAgent(
        jid=agents_config["email"][0],
        password=passwords["email"],
        provider=provider,
        system_prompt=EMAIL_MANAGER_PROMPT,
        tools=[human_tool],  # HITL capability
        mcp_servers=[gmail_mcp],
        termination_markers=["<EMAIL_PROCESS_COMPLETE>"],  # End conversation after email process
        verify_security=False
        # No reply_to - end of chain
    )

    
    # Start all agents
    print("\n🚀 Starting agents...")
    agents = {
        "chat": user_chat,
        "analyzer": analyzer_agent, 
        "notion": notion_agent,
        "email": email_agent,
    }
    
    for name, agent in agents.items():
        await agent.start()
        print(f"✅ {name.capitalize()} agent started")
    
    # Wait for connections
    await asyncio.sleep(3.0)
    
    print("\n" + "="*70)
    print("🐙 GITHUB ISSUES/PRS MONITOR SYSTEM")
    print("="*70)
    print("\n🎯 What this system does:")
    print("1. 📊 Analyzes GitHub issues and pull requests")
    print("2. 📚 Stores summaries in Notion database")
    print("3. 🤔 Asks human expert about email notifications")
    print("4. 📧 Sends professional summaries via Gmail")
    print("\n🛡️ Guardrails: Only GitHub-related requests accepted")
    print("\n💡 Example requests:")
    print("• 'Show me recent issues in the repository'")
    print("• 'Analyze pull requests from this week'")
    print("• 'Review GitHub activity and send summary'")
    print("\n⚠️  Note: All MCP services use Composio HTTP streaming.")
    print("Ensure human expert is available for email confirmations.")
    print("\nType 'exit' to quit\n")
    print("-" * 70)


    

    
    await user_chat.start()

    
    # Instructions for human expert
    print(f"\n👤 Human Expert Instructions:")
    print(f"🌐 Open web interface: http://localhost:8080")
    print(f"🔑 Connect as: {agents_config['human'][0]}")
    print("📧 You'll be asked about email sending decisions")
    
    try:
        # Run interactive chat
        await user_chat.run_interactive(
            input_prompt="🐙 GitHub> ",
            exit_command="exit",
            response_timeout=120.0  # Longer timeout for multi-agent processing
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    finally:
        # Stop all agents
        print("\n🔄 Stopping agents...")
        await user_chat.stop()
        for name, agent in agents.items():
            await agent.stop()
            print(f"✅ {name.capitalize()} agent stopped")
    
    print("\n✅ GitHub Monitor system shutdown complete!")


if __name__ == "__main__":
    print("🚀 Starting GitHub Issues/PRs Monitor...")
    print("\n📋 Prerequisites:")
    print("• OpenAI API key")
    print("• XMPP server running")
    print("• Internet connection for Composio MCP services")
    print("• Human expert web interface: python -m spade_llm.human_interface.web_server")
    print()
    
    try:
        spade.run(main())
    except KeyboardInterrupt:
        print("\n👋 Example terminated by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print("💡 Check your configuration and try again")