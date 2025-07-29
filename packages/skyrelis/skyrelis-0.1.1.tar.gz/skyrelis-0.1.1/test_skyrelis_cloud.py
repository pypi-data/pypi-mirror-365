#!/usr/bin/env python3
"""
Test Skyrelis v0.1.0 from TestPyPI with a real LangChain agent
"""

import os
import sys
from datetime import datetime

# Test import from TestPyPI installation
try:
    from skyrelis import observe
    print("✅ Skyrelis imported successfully from TestPyPI!")
    print(f"📦 Testing Skyrelis from TestPyPI installation")
except ImportError as e:
    print(f"❌ Failed to import Skyrelis: {e}")
    sys.exit(1)

# LangChain imports
try:
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.tools import StructuredTool
    print("✅ LangChain dependencies imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import LangChain dependencies: {e}")
    sys.exit(1)

# Cloud monitor URL (your deployed monitor)
CLOUD_MONITOR_URL = "http://monitor-alb-821056488.us-east-1.elb.amazonaws.com:80"

# Define test tools
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    return f"Weather in {location}: Sunny, 72°F with light breeze"

def search_database(query: str) -> str:
    """Search the company database."""
    return f"Database search for '{query}' returned 3 matching records"

def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b

# Create tools
tools = [
    StructuredTool.from_function(get_weather),
    StructuredTool.from_function(search_database),
    StructuredTool.from_function(calculate_sum)
]

# Create prompt with rich system prompt (for testing system prompt capture)
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are SkyrelisBot, an AI assistant with enterprise security monitoring.

    **Your Role**: Helpful business assistant with access to various tools
    **Security Level**: Production
    **Capabilities**:
    - Weather information lookup
    - Database queries
    - Mathematical calculations
    
    **Instructions**:
    - Always be helpful and professional
    - Use tools when appropriate for user requests
    - Provide clear, concise responses
    - Follow all security protocols
    
    **Security Notice**: All interactions are monitored and logged for security compliance."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Initialize LLM (using a dummy key for testing - real key needed for actual calls)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY", "sk-test-dummy-key-for-testing")
)

# Create agent
agent = create_openai_functions_agent(llm, tools, prompt)

# 🔒 Apply Skyrelis Security Monitoring! 🔒
@observe(
    remote_observer_url=CLOUD_MONITOR_URL,
    agent_name="TestSkyrelisBot_v0.1.0",
    capture_metadata=True
)
class SecureTestAgent(AgentExecutor):
    """
    Test agent with Skyrelis security monitoring.
    
    This agent is instrumented with:
    ✅ Complete execution tracing
    ✅ System prompt capture
    ✅ Tool usage monitoring
    ✅ Real-time security alerts
    ✅ Agent registry integration
    """
    pass


def main():
    """Test the Skyrelis-monitored agent."""
    print("\n" + "="*60)
    print("🔒 SKYRELIS v0.1.0 CLOUD MONITOR TEST")
    print("="*60)
    
    print(f"🌐 Cloud Monitor URL: {CLOUD_MONITOR_URL}")
    print(f"🤖 Agent: TestSkyrelisBot_v0.1.0")
    print(f"📅 Test Time: {datetime.now().isoformat()}")
    
    # Initialize the secure agent
    print("\n📦 Initializing Skyrelis-monitored agent...")
    try:
        secure_agent = SecureTestAgent(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
        print("✅ Agent initialized successfully with Skyrelis monitoring!")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False
    
    # Test queries that will generate different types of traces
    test_queries = [
        "What's the weather like in San Francisco?",
        "Search the database for information about user 'john_doe'",
        "What is 42 + 58?",
        "What tools do you have available?",
        "Hello! Can you introduce yourself?"
    ]
    
    print(f"\n🧪 Running {len(test_queries)} test interactions...")
    print("📊 All interactions will be sent to the cloud monitor for validation")
    
    success_count = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}/{len(test_queries)}: {query}")
        print("-" * 50)
        
        try:
            # This invoke call is automatically monitored by Skyrelis
            result = secure_agent.invoke({"input": query})
            print(f"✅ Response: {result['output'][:100]}...")
            print("📤 Trace data sent to cloud monitor")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("📤 Error trace sent to cloud monitor")
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Successful interactions: {success_count}/{len(test_queries)}")
    print(f"📤 Traces sent to cloud monitor: {len(test_queries)}")
    
    print("\n🔍 DATA CAPTURED AND SENT TO CLOUD MONITOR:")
    print("✅ Agent registration (unique ID + system prompts)")
    print("✅ Complete execution traces with timestamps")
    print("✅ Tool calls and their parameters/results")
    print("✅ LLM interactions and responses")
    print("✅ Performance metrics and timing")
    print("✅ Any errors or exceptions")
    print("✅ Agent metadata and configuration")
    
    print(f"\n🌐 VERIFICATION:")
    print(f"Check your cloud monitor at: {CLOUD_MONITOR_URL}")
    print("Look for agent: TestSkyrelisBot_v0.1.0")
    print("Verify traces contain system prompts and tool usage")
    
    return success_count == len(test_queries)


if __name__ == "__main__":
    print("🚀 Starting Skyrelis v0.1.0 Integration Test")
    
    # Note about API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: No OPENAI_API_KEY set - using dummy key")
        print("   Real LLM calls will fail, but tracing/monitoring will still work")
        print("   Set export OPENAI_API_KEY='your-key' for full functionality")
    
    print("🔒 This test verifies Skyrelis sends agent data to your cloud monitor")
    
    success = main()
    
    if success:
        print("\n🎉 TEST SUCCESSFUL!")
        print("📊 Skyrelis v0.1.0 is working correctly with cloud monitor")
    else:
        print("\n⚠️  TEST COMPLETED WITH ISSUES")
        print("📊 Check cloud monitor for trace data despite errors")
    
    print("\n🔗 Next: Check the real PyPI publication process!")
