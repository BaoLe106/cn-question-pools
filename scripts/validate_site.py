from __future__ import annotations

import json
from pathlib import Path


root = Path(__file__).resolve().parents[1]
prefix = "window.FLASHCARD_MODULES=window.FLASHCARD_MODULES||[];window.FLASHCARD_MODULES.push("

total = 0
for module_number, expected_count in ((1, 35), (2, 55), (3, 30)):
    source = (root / "data" / f"module-{module_number}.js").read_text(encoding="utf-8")
    assert source.startswith(prefix) and source.endswith(");\n")
    module = json.loads(source[len(prefix) : -3])
    assert len(module["cards"]) == expected_count
    assert [card["number"] for card in module["cards"]] == list(range(1, expected_count + 1))
    for card in module["cards"]:
        assert card["question"] and card["answer"] and card["explanation"] and card["topic"]
        expected_choices = 4 if card["type"] == "MCQ" else 2
        assert len(card["choices"]) == expected_choices, card["id"]
        assert card["answer"] in {choice["label"] for choice in card["choices"]}, card["id"]
        assert "PAGE BREAK" not in json.dumps(card)
        if card["image"]:
            assert (root / card["image"]).is_file(), card["id"]
            assert card["imageAlt"], card["id"]
    total += len(module["cards"])
    topics = sorted({card["topic"] for card in module["cards"]})
    print(f"Module {module_number}: {len(module['cards'])} cards, {len(topics)} topics")
    for topic in topics:
        print(f"  - {topic}")

assert total == 120
print(f"Validated {total} cards.")
