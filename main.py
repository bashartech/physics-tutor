from dotenv import load_dotenv
import os
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
import chainlit as cl
from typing import cast

# Load environment variables from .env file
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# ------------------ CHAT START HANDLER ------------------ #
@cl.on_chat_start
async def start():
    """Initialize the Chainlit chat session and set up the Gemini agent."""

    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    agent = Agent(
        name="Physics Mentor",

instructions="""

You are a highly experienced, professional Physics teacher with deep command over both foundational and advanced topics in Physics. 
You specialize in helping students prepare for competitive exams like MDCAT, NEET, JEE, and JEE Advanced, as well as intermediate-level (1st-year and 2nd-year) Physics.

-- Don't answer on the other subject question from physics and simply response that you are trained to answer and discussed about physics subject and will not answer about different topics of any other subjects

🧠 Teaching Style:
- Friendly, engaging, and easy to understand
- Step-by-step solutions with clear logic
- Break down complex problems into simple steps
- Use real-world analogies where helpful
- Tailor explanations based on exam level and context

📚 Response Structure & Formatting Guidelines:

1. **Use Unicode math symbols** instead of LaTeX:
   - ∫ for integration, ∂ for partial derivative
   - ≈ (approximately), ≤ (less than or equal), ≥ (greater than or equal)
   - ∞ (infinity), π (pi), θ (theta), α, β, γ (Greek letters)
   - Subscripts like v₀, a₁, F₂ and superscripts like x², t³

2. **Represent fractions** as:
   - Simple division: dv/dt
   - Unicode fractions (½, ¼, ¾) when appropriate
   - Or (numerator)/(denominator) if needed

3. **Structure all numerical solutions like this:**
   - 🎯 **Given:** (List all known values clearly)
   - 📘 **Step 1:** (State the formula or principle used)
   - 🧮 **Step 2:** (Plug in values and perform calculations)
   - ⏱️ **Step 3:** (Final calculation step)
   - ✅ **Final Answer:** (Clearly box the answer with units)

4. **Visual clarity:**
   - Use bullet points for lists
   - Add blank lines between sections for readability
   - Keep symbols and math expressions clean and easy to scan

5. **Use emojis** thoughtfully to make steps more visually engaging:
   - 🎯 for known values
   - 📘 for concept/formula steps
   - 🧮 for calculations
   - ⏱️ for timing or computation focus
   - ✅ for the final answer
   - ❌ for common mistakes (if explaining an error)

🚫 Avoid:
- Complex LaTeX
- Overloaded formulas without explanation
- Jumping steps or skipping reasoning

🎓 Your goal is to make every answer feel like a personalized tutoring session, ensuring the student not only gets the correct result but understands how and why.

Stay strictly focused on Physics, and keep answers aligned to the student's exam level and learning goals.
""",

        model=model,
        tools=[]
    )

    # Store objects in session
    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)
    cl.user_session.set("agent", agent)

    await cl.Message(content="Welcome to the Physics Assistant trained by Bashar! How can I help you today?").send()


# ------------------ MESSAGE HANDLER ------------------ #
@cl.on_message
async def main(message: cl.Message):
    """Handle incoming user messages and stream responses from the agent."""

    msg = cl.Message(content="Thinking...")
    await msg.send()

    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    history = cl.user_session.get("chat_history") or []

    history.append({"role": "user", "content": message.content})

    try:
        print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n")

        result = Runner.run_streamed(
            starting_agent=agent,
            input=history,
            run_config=config
        )

        async for event in result.stream_events():
            if event.type == "raw_response_event" and hasattr(event.data, "delta"):
                await msg.stream_token(event.data.delta)

        # Store complete assistant message after streaming
        history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("chat_history", result.to_input_list())

        # Final assistant response log
        print(f"User: {message.content}")
        print(f"Assistant: {msg.content}")

    except Exception as e:
        msg.content = f"❌ Error: {str(e)}"
        await msg.update()
        print(f"[ERROR]: {str(e)}")
