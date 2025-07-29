# Community Packs: Domain-Specific Prompt Templates & Schemas

Prompter supports a growing ecosystem of community-contributed packs containing prompt templates and Python schema classes for domain-specific LLM use cases. Packs make it easy to share, reuse, and standardize best-practice prompts and output structures for any field—SRE, Risk, Compliance, HR, Finance, and more.

## Benefits
- **Plug-and-play**: Instantly use high-quality, field-tested prompts and schemas.
- **Consistency**: Standardize LLM usage and output across your team or industry.
- **Extensibility**: Mix and match packs, or create your own for any domain.
- **Community-driven**: Leverage and contribute to a shared knowledge base.

## Example: SRE Incident Response Pack

**Directory structure:**
```
prompter_sre_templates/
  templates/
    incident_response.prompt
    monitoring.prompt
  schemas/
    incident_response.py
    monitoring.py
```

**incident_response.prompt**
```
Incident: {{incident}}
Context: {{context}}
Action Plan:
```

**incident_response.py**
```python
from pydantic import BaseModel

class IncidentResponse(BaseModel):
    action_plan: str
    severity: str
```

**Usage:**
```python
from prompter.prompt_template_processor import PromptTemplateProcessor
from prompter_sre_templates.schemas.incident_response import IncidentResponse

# Load template from the pack
processor = PromptTemplateProcessor('incident_response.prompt', package='prompter_sre_templates.templates')
prompt = processor.render({'incident': 'DB outage', 'context': 'Production'})

# Use schema for structured output
response = service.generate(prompt, result_object=IncidentResponse)
print(response.action_plan, response.severity)
```

## Example: Finance Compliance Pack

**Directory structure:**
```
prompter_finance_templates/
  templates/
    risk_assessment.prompt
  schemas/
    risk_assessment.py
```

**risk_assessment.prompt**
```
Transaction: {{transaction}}
Regulations: {{regulations}}
Risk Assessment:
```

**risk_assessment.py**
```python
from dataclasses import dataclass

@dataclass
class RiskAssessment:
    risk_level: str
    notes: str
```

## How to Create a Pack
1. **Create a new Python package (e.g., `prompter_sre_templates`).**
2. **Add a `templates/` folder for your prompt files.**
3. **Add a `schemas/` folder for your Python dataclasses or Pydantic models.**
4. **(Optional) Add entry points in `pyproject.toml` for plugin discovery.**
5. **Publish your pack to PyPI for easy sharing.**

## Tips
- You can include both templates and schema classes in a single pack, or split them into separate packs.
- Use clear, descriptive names for templates and schema classes.
- Document your pack with usage examples and field descriptions.

## More Domain Examples
- **HR**: onboarding.prompt, candidate_evaluation.py
- **Compliance**: audit_checklist.prompt, audit_result.py
- **Risk**: risk_matrix.prompt, risk_matrix.py
- **Custom**: Any field or workflow you want to standardize!

## Contribute
Want your pack featured? Open a PR or issue with a link and description!
