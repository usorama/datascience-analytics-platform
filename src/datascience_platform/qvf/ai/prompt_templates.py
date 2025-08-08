"""QVF Prompt Templates for Ollama

This module contains optimized prompt templates for QVF semantic analysis.
The prompts are designed to extract structured information from work items
to enhance the mathematical QVF scoring with AI-powered insights.

Key Features:
- Structured output formats for consistent parsing
- Few-shot examples for better accuracy
- Domain-specific context for Agile/SAFe environments
- Temperature and parameter optimization
- Response validation patterns
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class AnalysisType(Enum):
    """Types of QVF analysis supported."""
    BUSINESS_VALUE = "business_value"
    STRATEGIC_ALIGNMENT = "strategic_alignment" 
    RISK_ASSESSMENT = "risk_assessment"
    COMPLEXITY_ANALYSIS = "complexity_analysis"
    FINANCIAL_IMPACT = "financial_impact"
    STAKEHOLDER_IMPACT = "stakeholder_impact"


@dataclass
class PromptConfig:
    """Configuration for prompt generation."""
    temperature: float = 0.3
    max_tokens: int = 1000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class QVFPromptTemplates:
    """Optimized prompt templates for QVF semantic analysis."""
    
    # System prompts for different analysis types
    SYSTEM_PROMPTS = {
        AnalysisType.BUSINESS_VALUE: """You are a business value analyst for Agile Release Trains. 
Your role is to assess work items for their potential business value and impact.

Key principles:
- Focus on measurable business outcomes
- Consider both direct and indirect value
- Account for strategic vs tactical value
- Assess value realization timeline
- Consider customer and stakeholder impact

Provide structured, objective analysis based on the work item description.""",

        AnalysisType.STRATEGIC_ALIGNMENT: """You are a strategic alignment expert for SAFe enterprises.
Your role is to assess how well work items align with strategic objectives and business goals.

Key principles:
- Evaluate alignment with PI objectives
- Assess contribution to business outcomes
- Consider portfolio-level strategic themes
- Account for architectural alignment
- Evaluate organizational capability building

Provide structured analysis of strategic fit and alignment.""",

        AnalysisType.RISK_ASSESSMENT: """You are a risk analysis expert for software development.
Your role is to identify and assess risks associated with work items.

Key principles:
- Identify technical, business, and operational risks
- Assess probability and impact
- Consider dependencies and constraints
- Evaluate mitigation strategies
- Account for uncertainty and unknowns

Provide structured risk assessment with severity levels.""",

        AnalysisType.COMPLEXITY_ANALYSIS: """You are a technical complexity analyst for software development.
Your role is to assess the technical complexity and effort requirements of work items.

Key principles:
- Evaluate technical complexity factors
- Assess skill requirements and availability
- Consider integration complexity
- Account for testing and deployment complexity
- Identify architectural impacts

Provide structured complexity assessment with effort indicators.""",

        AnalysisType.FINANCIAL_IMPACT: """You are a financial impact analyst for technology investments.
Your role is to assess the financial implications of work items.

Key principles:
- Identify revenue impact (positive/negative)
- Assess cost savings opportunities
- Consider investment requirements
- Evaluate ROI potential
- Account for operational cost changes

Provide structured financial impact analysis.""",

        AnalysisType.STAKEHOLDER_IMPACT: """You are a stakeholder impact analyst for enterprise initiatives.
Your role is to assess how work items impact different stakeholders.

Key principles:
- Identify affected stakeholder groups
- Assess positive and negative impacts
- Consider change management implications
- Evaluate communication requirements
- Account for training and adoption needs

Provide structured stakeholder impact assessment."""
    }

    @classmethod
    def get_business_value_prompt(cls, work_item: Dict[str, Any]) -> str:
        """Generate business value analysis prompt."""
        title = work_item.get('title', 'N/A')
        description = work_item.get('description', 'N/A')
        acceptance_criteria = work_item.get('acceptance_criteria', 'N/A')
        
        return f"""Analyze the business value of this work item:

**Title:** {title}
**Description:** {description}
**Acceptance Criteria:** {acceptance_criteria}

Please provide a structured analysis in the following JSON format:

{{
    "business_value_score": <1-10 integer score>,
    "value_drivers": [
        {{
            "driver": "<specific value driver>",
            "impact": "<High/Medium/Low>",
            "rationale": "<explanation>"
        }}
    ],
    "customer_impact": {{
        "direct_impact": "<description>",
        "indirect_impact": "<description>",
        "impact_timeline": "<Immediate/Short-term/Long-term>"
    }},
    "revenue_potential": {{
        "revenue_category": "<Revenue Generation/Cost Reduction/Risk Mitigation/Strategic>",
        "confidence": "<High/Medium/Low>",
        "rationale": "<explanation>"
    }},
    "competitive_advantage": {{
        "provides_advantage": <true/false>,
        "advantage_type": "<Feature Parity/Differentiation/Innovation>",
        "sustainability": "<High/Medium/Low>"
    }},
    "key_insights": [
        "<insight 1>",
        "<insight 2>",
        "<insight 3>"
    ],
    "confidence_level": <1-10 integer score>
}}

Focus on measurable business outcomes and be specific in your analysis."""

    @classmethod
    def get_strategic_alignment_prompt(cls, work_item: Dict[str, Any], strategic_context: Optional[Dict] = None) -> str:
        """Generate strategic alignment analysis prompt."""
        title = work_item.get('title', 'N/A')
        description = work_item.get('description', 'N/A')
        
        context_section = ""
        if strategic_context:
            pi_objectives = strategic_context.get('pi_objectives', [])
            business_outcomes = strategic_context.get('business_outcomes', [])
            
            if pi_objectives:
                context_section += f"\n**PI Objectives:** {', '.join(pi_objectives)}"
            if business_outcomes:
                context_section += f"\n**Business Outcomes:** {', '.join(business_outcomes)}"
        
        return f"""Analyze the strategic alignment of this work item:

**Title:** {title}
**Description:** {description}{context_section}

Please provide a structured analysis in the following JSON format:

{{
    "strategic_alignment_score": <1-10 integer score>,
    "alignment_factors": [
        {{
            "factor": "<strategic factor>",
            "alignment_strength": "<Strong/Moderate/Weak>",
            "rationale": "<explanation>"
        }}
    ],
    "pi_objective_alignment": [
        {{
            "objective": "<PI objective>",
            "contribution_level": "<High/Medium/Low>",
            "contribution_type": "<Direct/Indirect/Enabling>"
        }}
    ],
    "business_outcome_impact": [
        {{
            "outcome": "<business outcome>",
            "impact_type": "<Accelerates/Enables/Supports>",
            "impact_magnitude": "<High/Medium/Low>"
        }}
    ],
    "architectural_alignment": {{
        "supports_target_architecture": <true/false>,
        "architectural_impact": "<Positive/Neutral/Negative>",
        "technical_debt_impact": "<Reduces/Neutral/Increases>"
    }},
    "portfolio_coherence": {{
        "fits_portfolio_strategy": <true/false>,
        "synergy_opportunities": ["<opportunity 1>", "<opportunity 2>"],
        "dependency_alignment": "<Well-aligned/Moderately-aligned/Poorly-aligned>"
    }},
    "key_insights": [
        "<insight 1>",
        "<insight 2>",
        "<insight 3>"
    ],
    "confidence_level": <1-10 integer score>
}}

Focus on how this work item advances strategic objectives and business outcomes."""

    @classmethod
    def get_risk_assessment_prompt(cls, work_item: Dict[str, Any]) -> str:
        """Generate risk assessment prompt."""
        title = work_item.get('title', 'N/A')
        description = work_item.get('description', 'N/A')
        dependencies = work_item.get('dependencies', 'N/A')
        
        return f"""Analyze the risks associated with this work item:

**Title:** {title}
**Description:** {description}
**Dependencies:** {dependencies}

Please provide a structured analysis in the following JSON format:

{{
    "overall_risk_score": <1-10 integer score>,
    "risk_factors": [
        {{
            "risk_category": "<Technical/Business/Operational/External>",
            "risk_description": "<specific risk>",
            "probability": "<High/Medium/Low>",
            "impact": "<High/Medium/Low>",
            "risk_score": <1-10 integer>,
            "mitigation_strategies": ["<strategy 1>", "<strategy 2>"]
        }}
    ],
    "technical_risks": [
        {{
            "risk": "<technical risk>",
            "complexity_factor": "<High/Medium/Low>",
            "skill_availability": "<Available/Limited/Unavailable>",
            "technology_maturity": "<Mature/Emerging/Experimental>"
        }}
    ],
    "business_risks": [
        {{
            "risk": "<business risk>",
            "market_impact": "<High/Medium/Low>",
            "stakeholder_impact": "<High/Medium/Low>",
            "timeline_sensitivity": "<Critical/Important/Flexible>"
        }}
    ],
    "dependency_risks": [
        {{
            "dependency": "<dependency>",
            "dependency_risk": "<High/Medium/Low>",
            "impact_if_delayed": "<High/Medium/Low>",
            "mitigation_options": ["<option 1>", "<option 2>"]
        }}
    ],
    "risk_mitigation_plan": {{
        "primary_mitigations": ["<mitigation 1>", "<mitigation 2>"],
        "contingency_plans": ["<plan 1>", "<plan 2>"],
        "monitoring_indicators": ["<indicator 1>", "<indicator 2>"]
    }},
    "confidence_level": <1-10 integer score>
}}

Focus on identifying actionable risks with specific mitigation strategies."""

    @classmethod
    def get_complexity_analysis_prompt(cls, work_item: Dict[str, Any]) -> str:
        """Generate complexity analysis prompt."""
        title = work_item.get('title', 'N/A')
        description = work_item.get('description', 'N/A')
        acceptance_criteria = work_item.get('acceptance_criteria', 'N/A')
        
        return f"""Analyze the technical complexity of this work item:

**Title:** {title}
**Description:** {description}
**Acceptance Criteria:** {acceptance_criteria}

Please provide a structured analysis in the following JSON format:

{{
    "complexity_score": <1-10 integer score>,
    "complexity_factors": [
        {{
            "factor": "<complexity factor>",
            "complexity_level": "<High/Medium/Low>",
            "rationale": "<explanation>",
            "effort_multiplier": <decimal multiplier>
        }}
    ],
    "technical_complexity": {{
        "algorithmic_complexity": "<High/Medium/Low>",
        "integration_complexity": "<High/Medium/Low>",
        "data_complexity": "<High/Medium/Low>",
        "ui_complexity": "<High/Medium/Low>",
        "infrastructure_complexity": "<High/Medium/Low>"
    }},
    "skill_requirements": [
        {{
            "skill": "<required skill>",
            "proficiency_level": "<Expert/Advanced/Intermediate/Basic>",
            "availability": "<Available/Limited/Unavailable>",
            "learning_curve": "<Steep/Moderate/Gentle>"
        }}
    ],
    "effort_estimation": {{
        "base_effort": "<story points or days>",
        "complexity_multiplier": <decimal>,
        "adjusted_effort": "<adjusted estimate>",
        "confidence": "<High/Medium/Low>"
    }},
    "implementation_challenges": [
        {{
            "challenge": "<specific challenge>",
            "difficulty": "<High/Medium/Low>",
            "solution_approach": "<suggested approach>"
        }}
    ],
    "testing_complexity": {{
        "unit_testing": "<High/Medium/Low>",
        "integration_testing": "<High/Medium/Low>",
        "performance_testing": "<Required/Optional/Not-needed>",
        "user_acceptance_testing": "<Complex/Standard/Simple>"
    }},
    "key_insights": [
        "<insight 1>",
        "<insight 2>",
        "<insight 3>"
    ],
    "confidence_level": <1-10 integer score>
}}

Focus on technical factors that impact implementation effort and success."""

    @classmethod
    def get_financial_impact_prompt(cls, work_item: Dict[str, Any]) -> str:
        """Generate financial impact analysis prompt."""
        title = work_item.get('title', 'N/A')
        description = work_item.get('description', 'N/A')
        
        return f"""Analyze the financial impact of this work item:

**Title:** {title}
**Description:** {description}

Please provide a structured analysis in the following JSON format:

{{
    "financial_impact_score": <1-10 integer score>,
    "revenue_impact": {{
        "revenue_type": "<Direct Revenue/Revenue Enabler/Revenue Protection/Cost Avoidance>",
        "impact_magnitude": "<High/Medium/Low>",
        "timeline": "<Immediate/Short-term/Medium-term/Long-term>",
        "confidence": "<High/Medium/Low>",
        "rationale": "<explanation>"
    }},
    "cost_impact": {{
        "cost_category": "<Development/Operational/Maintenance/Infrastructure>",
        "cost_change": "<Increase/Decrease/Neutral>",
        "magnitude": "<High/Medium/Low>",
        "recurring": <true/false>
    }},
    "roi_indicators": [
        {{
            "indicator": "<ROI indicator>",
            "measurement": "<how to measure>",
            "expected_value": "<expected outcome>",
            "timeframe": "<when to measure>"
        }}
    ],
    "investment_requirements": {{
        "development_cost": "<High/Medium/Low/Unknown>",
        "infrastructure_cost": "<High/Medium/Low/None>",
        "training_cost": "<High/Medium/Low/None>",
        "ongoing_costs": "<High/Medium/Low/None>"
    }},
    "financial_risks": [
        {{
            "risk": "<financial risk>",
            "probability": "<High/Medium/Low>",
            "potential_impact": "<cost/revenue impact>",
            "mitigation": "<mitigation strategy>"
        }}
    ],
    "business_case_strength": {{
        "payback_period": "<Quick/Moderate/Long/Unknown>",
        "business_justification": "<Strong/Moderate/Weak>",
        "financial_certainty": "<High/Medium/Low>"
    }},
    "key_insights": [
        "<insight 1>",
        "<insight 2>",
        "<insight 3>"
    ],
    "confidence_level": <1-10 integer score>
}}

Focus on quantifiable financial impacts and business value creation."""

    @classmethod
    def get_stakeholder_impact_prompt(cls, work_item: Dict[str, Any]) -> str:
        """Generate stakeholder impact analysis prompt."""
        title = work_item.get('title', 'N/A')
        description = work_item.get('description', 'N/A')
        
        return f"""Analyze the stakeholder impact of this work item:

**Title:** {title}
**Description:** {description}

Please provide a structured analysis in the following JSON format:

{{
    "stakeholder_impact_score": <1-10 integer score>,
    "affected_stakeholders": [
        {{
            "stakeholder_group": "<stakeholder group>",
            "impact_type": "<Positive/Negative/Mixed>",
            "impact_magnitude": "<High/Medium/Low>",
            "impact_description": "<specific impact>",
            "change_required": "<High/Medium/Low/None>"
        }}
    ],
    "customer_impact": {{
        "external_customers": {{
            "impact_type": "<Positive/Negative/Neutral>",
            "impact_areas": ["<area 1>", "<area 2>"],
            "adoption_effort": "<High/Medium/Low>"
        }},
        "internal_customers": {{
            "impact_type": "<Positive/Negative/Neutral>",
            "affected_teams": ["<team 1>", "<team 2>"],
            "workflow_changes": "<Major/Minor/None>"
        }}
    }},
    "organizational_impact": {{
        "process_changes": ["<process change 1>", "<process change 2>"],
        "skill_development_needs": ["<skill 1>", "<skill 2>"],
        "cultural_impact": "<High/Medium/Low>",
        "communication_complexity": "<High/Medium/Low>"
    }},
    "change_management": {{
        "change_readiness": "<High/Medium/Low>",
        "resistance_factors": ["<factor 1>", "<factor 2>"],
        "success_factors": ["<factor 1>", "<factor 2>"],
        "communication_strategy": "<Complex/Standard/Simple>"
    }},
    "support_requirements": {{
        "training_needed": "<Extensive/Moderate/Minimal/None>",
        "documentation_updates": "<Extensive/Moderate/Minimal/None>",
        "ongoing_support": "<High/Medium/Low>",
        "transition_support": "<Complex/Standard/Simple>"
    }},
    "stakeholder_alignment": {{
        "consensus_level": "<High/Medium/Low>",
        "conflicting_interests": ["<conflict 1>", "<conflict 2>"],
        "alignment_strategies": ["<strategy 1>", "<strategy 2>"]
    }},
    "key_insights": [
        "<insight 1>",
        "<insight 2>",
        "<insight 3>"
    ],
    "confidence_level": <1-10 integer score>
}}

Focus on identifying all affected parties and their specific impacts."""

    @classmethod
    def get_default_options(cls, analysis_type: AnalysisType) -> Dict[str, Any]:
        """Get default Ollama options for analysis type."""
        base_options = {
            "temperature": 0.3,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        }
        
        # Adjust parameters based on analysis type
        if analysis_type == AnalysisType.BUSINESS_VALUE:
            base_options.update({
                "temperature": 0.4,  # Slightly more creative for value insights
                "num_predict": 1200
            })
        elif analysis_type == AnalysisType.RISK_ASSESSMENT:
            base_options.update({
                "temperature": 0.2,  # More conservative for risk analysis
                "num_predict": 1000
            })
        elif analysis_type == AnalysisType.COMPLEXITY_ANALYSIS:
            base_options.update({
                "temperature": 0.3,  # Balanced for technical analysis
                "num_predict": 1100
            })
        elif analysis_type == AnalysisType.FINANCIAL_IMPACT:
            base_options.update({
                "temperature": 0.2,  # Conservative for financial analysis
                "num_predict": 1000
            })
        elif analysis_type == AnalysisType.STRATEGIC_ALIGNMENT:
            base_options.update({
                "temperature": 0.35,  # Balanced for strategic thinking
                "num_predict": 1200
            })
        elif analysis_type == AnalysisType.STAKEHOLDER_IMPACT:
            base_options.update({
                "temperature": 0.4,  # More creative for stakeholder analysis
                "num_predict": 1300
            })
        
        return base_options

    @classmethod
    def get_system_prompt(cls, analysis_type: AnalysisType) -> str:
        """Get system prompt for analysis type."""
        return cls.SYSTEM_PROMPTS.get(analysis_type, "You are a helpful assistant for work item analysis.")

    @classmethod
    def get_analysis_prompt(cls, 
                          analysis_type: AnalysisType, 
                          work_item: Dict[str, Any],
                          context: Optional[Dict[str, Any]] = None) -> str:
        """Get analysis prompt for the specified type."""
        if analysis_type == AnalysisType.BUSINESS_VALUE:
            return cls.get_business_value_prompt(work_item)
        elif analysis_type == AnalysisType.STRATEGIC_ALIGNMENT:
            return cls.get_strategic_alignment_prompt(work_item, context)
        elif analysis_type == AnalysisType.RISK_ASSESSMENT:
            return cls.get_risk_assessment_prompt(work_item)
        elif analysis_type == AnalysisType.COMPLEXITY_ANALYSIS:
            return cls.get_complexity_analysis_prompt(work_item)
        elif analysis_type == AnalysisType.FINANCIAL_IMPACT:
            return cls.get_financial_impact_prompt(work_item)
        elif analysis_type == AnalysisType.STAKEHOLDER_IMPACT:
            return cls.get_stakeholder_impact_prompt(work_item)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")

    @classmethod
    def validate_response_format(cls, response: str, analysis_type: AnalysisType) -> bool:
        """Validate that response matches expected JSON format."""
        try:
            import json
            data = json.loads(response)
            
            # Check for required fields based on analysis type
            required_fields = {
                AnalysisType.BUSINESS_VALUE: ["business_value_score", "value_drivers", "confidence_level"],
                AnalysisType.STRATEGIC_ALIGNMENT: ["strategic_alignment_score", "alignment_factors", "confidence_level"],
                AnalysisType.RISK_ASSESSMENT: ["overall_risk_score", "risk_factors", "confidence_level"],
                AnalysisType.COMPLEXITY_ANALYSIS: ["complexity_score", "complexity_factors", "confidence_level"],
                AnalysisType.FINANCIAL_IMPACT: ["financial_impact_score", "revenue_impact", "confidence_level"],
                AnalysisType.STAKEHOLDER_IMPACT: ["stakeholder_impact_score", "affected_stakeholders", "confidence_level"]
            }
            
            fields = required_fields.get(analysis_type, [])
            return all(field in data for field in fields)
            
        except (json.JSONDecodeError, KeyError, TypeError):
            return False