import os
from pathlib import Path

def load_prompt_file(filename: str) -> str:
    """prompt/ 디렉토리에서 프롬프트 파일을 로드합니다."""
    project_root = Path(__file__).parent.parent
    prompt_path = project_root / "prompt" / filename
    
    if prompt_path.exists():
        return prompt_path.read_text(encoding='utf-8').strip()
    else:
        raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {prompt_path}")

def get_system_prompt() -> str:
    """instructions.txt에서 시스템 프롬프트를 로드합니다."""
    return load_prompt_file("instructions.txt")

def get_fewshot_examples() -> str:
    """fewshot_examples.txt에서 예시를 로드합니다."""
    return load_prompt_file("fewshot_examples.txt")

def get_combined_prompt() -> str:
    """시스템 프롬프트와 예시를 결합하여 반환합니다."""
    instructions = get_system_prompt()
    examples = get_fewshot_examples()
    
    return f"{instructions}\n\n{examples}"