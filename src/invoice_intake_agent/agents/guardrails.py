"""Guardrails for the invoice intake agent."""

from agents import InputGuardrail, Agent, Runner, GuardrailFunctionOutput
from pydantic import BaseModel

from ..config import MODEL


class GuardrailOutput(BaseModel):
    """Output of the guardrail agent."""

    is_safe: bool
    reasoning: str


async def invoice_intake_guardrail(ctx, agent, input_data):
    """Guardrail for the invoice intake agent."""
    guardrail_agent = Agent(
        name="Guardrail check",
        instructions=(
            "Check if the input is asking about inappropiate content."
            "If so, return a tripwire triggered error."
        ),
        output_type=GuardrailOutput,
        model=str(MODEL),
    )
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(GuardrailOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_safe,
    )
