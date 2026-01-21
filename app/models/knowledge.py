"""
Knowledge Models for Tacit

Pydantic models for structured knowledge representation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class EmotionalWeight(str, Enum):
    HIGH = "높음"
    MEDIUM = "보통"
    LOW = "낮음"


class TransferDifficulty(str, Enum):
    HIGH = "상"
    MEDIUM = "중"
    LOW = "하"


class BusinessOpportunityType(str, Enum):
    KNOWLEDGE_TRANSFER = "지식전수형"
    CONTENT = "콘텐츠형"
    TOOL = "도구화형"
    SYSTEM = "시스템형"


# =============================================================================
# Phase 1: Socialization - Experience Map
# =============================================================================

class TacitKnowledgeCandidate(BaseModel):
    """암묵지 후보 영역"""
    area: str = Field(description="암묵지 후보 영역 이름")
    description: str = Field(description="해당 영역에 대한 간단한 설명")
    emotional_weight: EmotionalWeight = Field(description="자부심의 정도")
    evidence: str = Field(description="이 영역을 선택한 근거")


class UserProfile(BaseModel):
    """사용자 프로필"""
    role: str = Field(description="사용자의 직업/역할")
    experience_years: str = Field(description="경력 연수")
    domain: str = Field(description="전문 분야")


class ExperienceMap(BaseModel):
    """경험 지도 - 사회화 단계의 Output"""
    user_profile: UserProfile
    tacit_knowledge_candidates: List[TacitKnowledgeCandidate]
    recommended_focus: str = Field(description="가장 먼저 탐색할 영역과 그 이유")


# =============================================================================
# Phase 2: Externalization - Tacit Knowledge Specification
# =============================================================================

class TacitKnowledgeSpec(BaseModel):
    """암묵지 명세서 - 표출화 단계의 Output"""
    knowledge_name: str = Field(description="이 암묵지에 붙일 이름")
    summary: str = Field(description="한 문장으로 요약")
    detailed_description: str = Field(description="상세한 설명")

    trigger_signals: List[str] = Field(description="이 지식이 발동되는 신호/상황")
    decision_rules: List[str] = Field(description="추출된 판단 규칙")
    exceptions: List[str] = Field(description="예외 상황")

    metaphor: str = Field(description="이 지식을 표현하는 은유")
    sensory_cues: List[str] = Field(default=[], description="시각적/청각적/촉각적 단서")
    common_mistakes: List[str] = Field(default=[], description="초보자가 자주 하는 실수")

    transfer_difficulty: TransferDifficulty = Field(description="전달 난이도")
    transfer_method: str = Field(description="이 지식을 전달하기 위한 추천 방법")

    evidence_quotes: List[str] = Field(default=[], description="근거가 된 사용자 발언")


# =============================================================================
# Phase 3: Combination - Business Opportunity Card
# =============================================================================

class KnowledgeAssetScore(BaseModel):
    """지식 자산 점수"""
    name: str
    scarcity_score: int = Field(ge=1, le=5, description="희소성 점수")
    demand_score: int = Field(ge=1, le=5, description="수요 점수")
    transferability_score: int = Field(ge=1, le=5, description="전달 가능성 점수")


class BusinessOpportunity(BaseModel):
    """비즈니스 기회"""
    opportunity_name: str
    type: BusinessOpportunityType
    target_customer: str
    value_proposition: str
    product_format: str
    difficulty: TransferDifficulty
    first_step: str


class BusinessOpportunityCard(BaseModel):
    """비즈니스 기회 카드 - 연결화 단계의 Output"""
    knowledge_asset: KnowledgeAssetScore
    business_opportunities: List[BusinessOpportunity]
    recommended_opportunity: str


# =============================================================================
# Phase 4: Internalization - Action Plan
# =============================================================================

class Experiment(BaseModel):
    """실험"""
    experiment_name: str
    description: str
    expected_outcome: str
    success_criteria: str
    time_required: str
    resources_needed: str


class ValidationMetric(BaseModel):
    """검증 지표"""
    metric_name: str
    how_to_measure: str
    target_value: str


class FirstCustomer(BaseModel):
    """첫 번째 고객"""
    who: str
    why_them: str
    how_to_reach: str


class Obstacle(BaseModel):
    """장애물"""
    obstacle: str
    mitigation: str


class ActionPlan(BaseModel):
    """주간 액션플랜 - 내면화 단계의 Output"""
    selected_opportunity: str
    this_week_experiments: List[Experiment]
    validation_metrics: List[ValidationMetric]
    first_customer: FirstCustomer
    next_session_checklist: List[str]
    potential_obstacles: List[Obstacle]


# =============================================================================
# Challenger - Validation Report
# =============================================================================

class BiasCheckResult(str, Enum):
    FOUND = "발견됨"
    SUSPECTED = "의심됨"
    NONE = "없음"


class ConcernSeverity(str, Enum):
    HIGH = "높음"
    MEDIUM = "중간"
    LOW = "낮음"


class OverallAssessment(str, Enum):
    PASS = "통과"
    CAUTION = "주의"
    REVIEW_NEEDED = "재검토 필요"


class Concern(BaseModel):
    """우려 사항"""
    concern: str
    severity: ConcernSeverity
    evidence: str
    suggestion: str


class BiasCheck(BaseModel):
    """편향 체크"""
    survivorship_bias: BiasCheckResult
    attribution_error: BiasCheckResult
    market_illusion: BiasCheckResult
    competition_blindness: BiasCheckResult
    confirmation_bias: BiasCheckResult


class ValidationReport(BaseModel):
    """검증 보고서"""
    validation_target: str
    overall_assessment: OverallAssessment
    strengths: List[str]
    concerns: List[Concern]
    bias_check: BiasCheck
    questions_to_consider: List[str]
    recommendation: str
