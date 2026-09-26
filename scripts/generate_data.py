from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTRACTED_DIR = ROOT / "extracted"
DATA_DIR = ROOT / "data"

MODULES = {
    1: {
        "title": "Introduction, History & Internet Architecture",
        "accent": "#d95d39",
        "images": {
            9: "figure-da437203a4d6.png",
            21: "figure-922544c89752.jpeg",
            35: "figure-64f943a0a529.png",
        },
    },
    2: {
        "title": "Transport & Application Layers",
        "accent": "#176b87",
        "images": {
            5: "figure-a4ef854dfbcb.jpeg",
            24: "figure-970778dbf5a9.png",
            38: "figure-08e86e5d0a22.jpeg",
            39: "figure-08e86e5d0a22.jpeg",
            40: "figure-08e86e5d0a22.jpeg",
            41: "figure-08e86e5d0a22.jpeg",
            42: "figure-08e86e5d0a22.jpeg",
            44: "figure-db674305b7a9.png",
            46: "figure-fe46e05c40b5.jpeg",
            50: "figure-54333ba5864f.png",
            51: "figure-54333ba5864f.png",
            52: "figure-54333ba5864f.png",
            53: "figure-54333ba5864f.png",
        },
    },
    3: {
        "title": "Network Layer: Routing",
        "accent": "#7557a5",
        "images": {
            6: "figure-537b7997093c.jpeg",
            7: "figure-537b7997093c.jpeg",
            8: "figure-537b7997093c.jpeg",
            13: "figure-b270f98cd6f2.png",
            14: "figure-ec8a354cd991.jpeg",
            15: "figure-ec8a354cd991.jpeg",
            16: "figure-ec8a354cd991.jpeg",
            17: "figure-903972873113.jpeg",
            18: "figure-903972873113.jpeg",
            21: "figure-c08dce75fdb2.jpeg",
            26: "figure-bd209e69b983.jpeg",
        },
    },
}

QUESTION_RE = re.compile(r"^Q(\d+)\.\s+\[(MCQ|TF)\]\s*$")
ANSWER_RE = re.compile(r"^\s*Correct answer:\s*(.+?)\s*$")
FIGURE_RE = re.compile(r"^Figure:\s*(.+?)\s*$")
CHOICE_RE = re.compile(r"^•\s*(?:(?P<label>[A-D])\.\s*)?(?P<text>.*)$")


def is_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped == "--- PAGE BREAK ---" or len(stripped) > 100:
        return False
    if stripped.startswith(("Why:", "Correct answer:", "•", "Q", "Figure:")):
        return False
    # A few source section titles are phrased as questions (for example,
    # "Multiplexing: Why Do We Need It?"). Other terminal punctuation marks a
    # wrapped sentence rather than a heading.
    return stripped[-1] not in ".!,:;"


def join_wrapped(lines: list[str]) -> str:
    result = ""
    for raw in lines:
        line = raw.strip()
        if not line or line == "--- PAGE BREAK ---":
            continue
        if result.endswith("-") and line[:1].islower():
            result += line
        else:
            result += (" " if result else "") + line
    return result.strip()


def parse_module(module_number: int) -> dict[str, object]:
    lines = (EXTRACTED_DIR / f"module-{module_number}.txt").read_text(encoding="utf-8").splitlines()
    markers = [(index, QUESTION_RE.match(line)) for index, line in enumerate(lines)]
    markers = [(index, match) for index, match in markers if match]

    starts: list[tuple[int, int, re.Match[str], str | None]] = []
    current_topic = "General"
    for line_index, match in markers:
        candidate_index = line_index - 1
        while candidate_index >= 0 and not lines[candidate_index].strip():
            candidate_index -= 1
        heading_index = line_index
        if candidate_index >= 0 and is_heading(lines[candidate_index]):
            current_topic = lines[candidate_index].strip()
            heading_index = candidate_index
        starts.append((line_index, heading_index, match, current_topic))

    cards = []
    image_map: dict[int, str] = MODULES[module_number]["images"]
    for index, (line_index, _, match, topic) in enumerate(starts):
        end_index = starts[index + 1][1] if index + 1 < len(starts) else len(lines)
        block = [line for line in lines[line_index + 1 : end_index] if line.strip() != "--- PAGE BREAK ---"]

        answer_index = next(i for i, line in enumerate(block) if ANSWER_RE.match(line))
        answer_match = ANSWER_RE.match(block[answer_index])
        why_index = next(i for i, line in enumerate(block[answer_index + 1 :], answer_index + 1) if line.strip().startswith("Why:"))

        prompt_lines = block[:answer_index]
        figure_caption = None
        without_caption = []
        for line in prompt_lines:
            figure_match = FIGURE_RE.match(line.strip())
            if figure_match:
                figure_caption = figure_match.group(1)
            else:
                without_caption.append(line)

        stem_lines: list[str] = []
        choice_groups: list[tuple[str | None, list[str]]] = []
        active_choice: tuple[str | None, list[str]] | None = None
        for line in without_caption:
            choice_match = CHOICE_RE.match(line.strip())
            if choice_match:
                active_choice = (choice_match.group("label"), [choice_match.group("text")])
                choice_groups.append(active_choice)
            elif active_choice is not None:
                active_choice[1].append(line)
            else:
                stem_lines.append(line)

        choices = []
        for label, choice_lines in choice_groups:
            text = join_wrapped(choice_lines)
            choices.append({"label": label or text, "text": text})

        explanation_lines = block[why_index:]
        explanation_lines[0] = explanation_lines[0].split("Why:", 1)[1]
        number = int(match.group(1))
        image_filename = image_map.get(number)
        cards.append(
            {
                "id": f"m{module_number}-q{number}",
                "number": number,
                "type": match.group(2),
                "topic": topic,
                "question": join_wrapped(stem_lines),
                "choices": choices,
                "answer": answer_match.group(1).strip(),
                "explanation": join_wrapped(explanation_lines),
                "image": f"assets/images/{image_filename}" if image_filename else None,
                "imageAlt": figure_caption,
            }
        )

    module = MODULES[module_number]
    return {
        "id": module_number,
        "label": f"Module {module_number}",
        "title": module["title"],
        "accent": module["accent"],
        "cards": cards,
    }


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    totals = []
    for module_number in sorted(MODULES):
        module = parse_module(module_number)
        payload = json.dumps(module, ensure_ascii=False, separators=(",", ":"))
        output = DATA_DIR / f"module-{module_number}.js"
        output.write_text(
            "window.FLASHCARD_MODULES=window.FLASHCARD_MODULES||[];"
            f"window.FLASHCARD_MODULES.push({payload});\n",
            encoding="utf-8",
        )
        totals.append({"module": module_number, "cards": len(module["cards"])})
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
