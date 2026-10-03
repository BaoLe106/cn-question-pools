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
    4: {
        "title": "AS Relationships & Interdomain Routing",
        "accent": "#b66b25",
        "images": {2: "figure-382f85312457.jpg", 3: "figure-6b047e04ee8b.png", 4: "figure-dfc74d335799.jpg", 7: "figure-dfc74d335799.jpg", 9: "figure-cdd475578d01.png", 10: "figure-1bc83642e16a.png", 12: "figure-dfc74d335799.jpg", 13: "figure-dfc74d335799.jpg", 14: "figure-17d91ca27e70.png", 16: "figure-0bb2220ba725.png", 17: "figure-2d41b2ea770e.jpg", 18: "figure-4519b7861819.png", 19: "figure-2669edb4788a.png", 20: "figure-52c5a2f819a1.png", 23: "figure-93c951e56f5e.png", 26: "figure-bb75e24711bc.png", 28: "figure-2999d086b41c.png", 29: "figure-5290d6a00510.jpg", 30: "figure-2071bf267b28.png"},
    },
    5: {
        "title": "Router Design & Algorithms I",
        "accent": "#2f7f76",
        "images": {2: "figure-77a833829fbf.png", 6: "figure-3e1a3f26fbf2.jpg", 7: "figure-3e1a3f26fbf2.jpg", 10: "figure-952ad6b17c19.jpg", 11: "figure-70c1328395be.jpg", 13: "figure-a12765724627.png", 14: "figure-f0575cca4c02.png", 22: "figure-ed5995631439.jpg", 23: "figure-b9768a03f85d.png", 24: "figure-15c3a0195b91.png", 26: "figure-ed5995631439.jpg", 32: "figure-76e4ac915478.png", 33: "figure-29a7af4378c3.png", 34: "figure-60ecd2a79da6.png", 35: "figure-b4859dda0e62.png", 36: "figure-32fe5fd960b1.png", 37: "figure-32fe5fd960b1.png", 38: "figure-43340ccfc52a.png"},
    },
    6: {
        "title": "Router Design & Algorithms II",
        "accent": "#a84d73",
        "images": {1: "figure-c91a6e2891e6.png", 2: "figure-32a48e8ec260.png", 3: "figure-dfd79b91bfb6.jpg", 5: "figure-5dd12ce47f0c.png", 7: "figure-5fd10184bd42.png", 8: "figure-876136f58f4f.jpg", 9: "figure-4c877687ede4.jpg", 10: "figure-b2bba0067b99.png", 11: "figure-6b27214ed294.png", 12: "figure-122778bd5fb4.png", 13: "figure-ff2505c76db7.png", 14: "figure-cb9cb6c1c699.png", 15: "figure-b1581f95a900.png", 16: "figure-560e8d270d74.png", 17: "figure-560e8d270d74.png", 18: "figure-dcf88ffcf5f3.png", 19: "figure-af2bc374d94c.png", 20: "figure-ac89116da903.png", 22: "figure-a3b10547c62a.jpg", 23: "figure-838bfab16e22.png", 26: "figure-6f07451343a8.png", 27: "figure-419410fe66ce.png", 28: "figure-c114189c5b4a.png"},
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
