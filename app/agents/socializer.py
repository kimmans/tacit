"""
Socializer Agent - Originating Ba (창발의 장)

Phase 1 of SECI: Socialization (암묵지 → 암묵지)

Builds rapport with the user and explores areas where tacit knowledge
might be hidden. Creates an Experience Map as output.
"""

import json
from typing import List, Optional, Tuple
from anthropic import Anthropic

from prompts.seci_prompts import (
    SOCIALIZER_SYSTEM_PROMPT,
    SOCIALIZER_EXPERIENCE_MAP_PROMPT
)
from models.knowledge import ExperienceMap


class Socializer:
    """
    공감자 Agent - 사회화 단계를 담당

    역할:
    - 사용자와 라포 형성
    - 암묵지가 숨어있을 경험의 영역 탐색
    - 경험 지도(Experience Map) 생성
    """

    def __init__(self, client: Anthropic, model: str = "claude-sonnet-4-20250514"):
        self.client = client
        self.model = model
        self.conversation_history: List[dict] = []
        self.is_complete = False
        self.experience_map: Optional[ExperienceMap] = None

    def reset(self):
        """대화 초기화"""
        self.conversation_history = []
        self.is_complete = False
        self.experience_map = None

    def chat(self, user_message: str) -> Tuple[str, bool]:
        """
        사용자와 대화

        Args:
            user_message: 사용자 메시지

        Returns:
            Tuple[str, bool]: (AI 응답, 단계 완료 여부)
        """
        # 대화 히스토리에 사용자 메시지 추가
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Claude API 호출
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=SOCIALIZER_SYSTEM_PROMPT,
            messages=self.conversation_history
        )

        assistant_message = response.content[0].text

        # 대화 히스토리에 AI 응답 추가
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        # 충분한 정보가 모였는지 확인 (대화 턴 수 기반)
        # 최소 5턴 이상 대화하고, 암묵지 후보를 언급하면 완료 가능
        if len(self.conversation_history) >= 10:  # 5턴 = 10개 메시지
            if self._has_enough_information():
                self.is_complete = True

        return assistant_message, self.is_complete

    def _has_enough_information(self) -> bool:
        """충분한 정보가 수집되었는지 확인"""
        # 간단한 휴리스틱: 대화 내용에 특정 키워드가 있는지 확인
        full_conversation = " ".join([
            msg["content"] for msg in self.conversation_history
        ])

        keywords = ["직업", "일", "경험", "노하우", "잘하", "자부심", "후배", "동료"]
        found_keywords = sum(1 for kw in keywords if kw in full_conversation)

        return found_keywords >= 4

    def generate_experience_map(self) -> ExperienceMap:
        """
        경험 지도 생성

        Returns:
            ExperienceMap: 생성된 경험 지도
        """
        # 경험 지도 생성 프롬프트 추가
        messages = self.conversation_history + [{
            "role": "user",
            "content": SOCIALIZER_EXPERIENCE_MAP_PROMPT
        }]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=SOCIALIZER_SYSTEM_PROMPT,
            messages=messages
        )

        # JSON 파싱
        response_text = response.content[0].text

        # JSON 블록 추출
        json_str = self._extract_json(response_text)

        try:
            data = json.loads(json_str)
            self.experience_map = ExperienceMap(**data)
        except (json.JSONDecodeError, Exception) as e:
            # 파싱 실패 시 기본값 반환
            print(f"JSON 파싱 오류: {e}")
            self.experience_map = self._create_fallback_map(response_text)

        return self.experience_map

    def _extract_json(self, text: str) -> str:
        """텍스트에서 JSON 블록 추출"""
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

        return text

    def _create_fallback_map(self, text: str) -> ExperienceMap:
        """파싱 실패 시 기본 경험 지도 생성"""
        from models.knowledge import UserProfile, TacitKnowledgeCandidate, EmotionalWeight

        return ExperienceMap(
            user_profile=UserProfile(
                role="미확인",
                experience_years="미확인",
                domain="미확인"
            ),
            tacit_knowledge_candidates=[
                TacitKnowledgeCandidate(
                    area="추가 대화 필요",
                    description="경험 지도 생성을 위해 추가 대화가 필요합니다",
                    emotional_weight=EmotionalWeight.MEDIUM,
                    evidence="자동 생성됨"
                )
            ],
            recommended_focus="추가 대화를 통해 암묵지 영역을 탐색해주세요"
        )

    def get_conversation_summary(self) -> str:
        """대화 요약 반환"""
        if not self.conversation_history:
            return "아직 대화가 시작되지 않았습니다."

        summary_parts = []
        for i, msg in enumerate(self.conversation_history):
            role = "사용자" if msg["role"] == "user" else "공감자"
            # 긴 메시지는 앞부분만
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary_parts.append(f"{role}: {content}")

        return "\n".join(summary_parts)

    def force_complete(self):
        """강제로 단계 완료 처리"""
        self.is_complete = True
