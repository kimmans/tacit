"""
Utility functions for Tacit
"""

import json
from typing import Any, Dict, Optional


def extract_json_from_text(text: str) -> Optional[str]:
    """
    텍스트에서 JSON 블록 추출

    Args:
        text: JSON을 포함한 텍스트

    Returns:
        추출된 JSON 문자열 또는 None
    """
    # ```json ... ``` 블록 찾기
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            return text[start:end].strip()

    # ``` ... ``` 블록 찾기
    if "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end > start:
            return text[start:end].strip()

    # { ... } 찾기
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        return text[start:end]

    return None


def safe_json_loads(json_str: str) -> Optional[Dict[str, Any]]:
    """
    안전한 JSON 파싱

    Args:
        json_str: JSON 문자열

    Returns:
        파싱된 딕셔너리 또는 None
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    텍스트 자르기

    Args:
        text: 원본 텍스트
        max_length: 최대 길이
        suffix: 잘린 경우 붙일 접미사

    Returns:
        잘린 텍스트
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_conversation_for_export(messages: list) -> str:
    """
    대화 내용을 마크다운 형식으로 포맷

    Args:
        messages: 대화 메시지 리스트

    Returns:
        마크다운 형식 문자열
    """
    lines = ["# 대화 기록\n"]

    for msg in messages:
        role = "**사용자**" if msg["role"] == "user" else "**AI**"
        content = msg["content"]
        lines.append(f"{role}:\n\n{content}\n\n---\n")

    return "\n".join(lines)


def create_report_markdown(
    experience_map: Optional[Dict] = None,
    knowledge_spec: Optional[Dict] = None,
    business_card: Optional[Dict] = None,
    action_plan: Optional[Dict] = None
) -> str:
    """
    최종 보고서 마크다운 생성

    Args:
        experience_map: 경험 지도
        knowledge_spec: 암묵지 명세서
        business_card: 비즈니스 기회 카드
        action_plan: 액션플랜

    Returns:
        마크다운 형식 보고서
    """
    lines = [
        "# Tacit 지식창조 보고서\n",
        "*SECI 모델 기반 암묵지 발견 및 비즈니스 기회 도출*\n",
        "---\n"
    ]

    if experience_map:
        lines.append("## 1. 경험 지도 (Experience Map)\n")
        lines.append("### 사용자 프로필\n")
        profile = experience_map.get("user_profile", {})
        lines.append(f"- **역할**: {profile.get('role', 'N/A')}\n")
        lines.append(f"- **경력**: {profile.get('experience_years', 'N/A')}\n")
        lines.append(f"- **분야**: {profile.get('domain', 'N/A')}\n\n")

        lines.append("### 암묵지 후보 영역\n")
        for candidate in experience_map.get("tacit_knowledge_candidates", []):
            lines.append(f"- **{candidate.get('area', 'N/A')}**\n")
            lines.append(f"  - {candidate.get('description', '')}\n")
            lines.append(f"  - 감정적 무게: {candidate.get('emotional_weight', 'N/A')}\n\n")

        lines.append(f"### 추천 탐색 영역\n{experience_map.get('recommended_focus', '')}\n\n")

    if knowledge_spec:
        lines.append("## 2. 암묵지 명세서 (Tacit Knowledge Specification)\n")
        lines.append(f"### {knowledge_spec.get('knowledge_name', 'N/A')}\n")
        lines.append(f"{knowledge_spec.get('summary', '')}\n\n")
        lines.append(f"**상세 설명**: {knowledge_spec.get('detailed_description', '')}\n\n")

        lines.append("#### 발동 신호\n")
        for signal in knowledge_spec.get("trigger_signals", []):
            lines.append(f"- {signal}\n")

        lines.append("\n#### 판단 규칙\n")
        for rule in knowledge_spec.get("decision_rules", []):
            lines.append(f"- {rule}\n")

        lines.append("\n#### 예외 상황\n")
        for exc in knowledge_spec.get("exceptions", []):
            lines.append(f"- {exc}\n")

        lines.append(f"\n**은유**: {knowledge_spec.get('metaphor', 'N/A')}\n")
        lines.append(f"**전달 난이도**: {knowledge_spec.get('transfer_difficulty', 'N/A')}\n")
        lines.append(f"**추천 전달 방법**: {knowledge_spec.get('transfer_method', 'N/A')}\n\n")

    if business_card:
        lines.append("## 3. 비즈니스 기회 카드\n")
        for opp in business_card.get("business_opportunities", []):
            lines.append(f"### {opp.get('opportunity_name', 'N/A')}\n")
            lines.append(f"- **유형**: {opp.get('type', 'N/A')}\n")
            lines.append(f"- **타겟 고객**: {opp.get('target_customer', 'N/A')}\n")
            lines.append(f"- **가치 제안**: {opp.get('value_proposition', 'N/A')}\n")
            lines.append(f"- **상품 형태**: {opp.get('product_format', 'N/A')}\n")
            lines.append(f"- **난이도**: {opp.get('difficulty', 'N/A')}\n")
            lines.append(f"- **첫 번째 단계**: {opp.get('first_step', 'N/A')}\n\n")

    if action_plan:
        lines.append("## 4. 주간 액션플랜\n")
        lines.append("### 이번 주 실험\n")
        for exp in action_plan.get("this_week_experiments", []):
            lines.append(f"- [ ] **{exp.get('experiment_name', 'N/A')}**\n")
            lines.append(f"  - {exp.get('description', '')}\n")
            lines.append(f"  - 예상 소요: {exp.get('time_required', 'N/A')}\n\n")

        lines.append("### 검증 지표\n")
        for metric in action_plan.get("validation_metrics", []):
            lines.append(f"- **{metric.get('metric_name', 'N/A')}**: {metric.get('target_value', 'N/A')}\n")

    lines.append("\n---\n")
    lines.append("*Tacit - SECI 모델 기반 암묵지 발견 서비스*\n")

    return "".join(lines)
