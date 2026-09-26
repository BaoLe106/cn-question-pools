(() => {
  "use strict";

  const modules = (window.FLASHCARD_MODULES || []).sort((a, b) => a.id - b.id);
  const storageKey = "cn-field-notes-mastered-v1";
  const state = {
    moduleId: modules[0]?.id,
    index: 0,
    search: "",
    topic: "all",
    shuffled: false,
    shuffleOrder: [],
    mastered: new Set(JSON.parse(localStorage.getItem(storageKey) || "[]")),
  };

  const $ = (selector) => document.querySelector(selector);
  const elements = {
    moduleNav: $("#module-nav"),
    topicFilter: $("#topic-filter"),
    searchInput: $("#search-input"),
    flashcard: $("#flashcard"),
    emptyState: $("#empty-state"),
    deckKicker: $("#deck-kicker"),
    deckTitle: $("#deck-title"),
    currentPosition: $("#current-position"),
    filteredCount: $("#filtered-count"),
    questionLabel: $("#question-label"),
    backQuestionLabel: $("#back-question-label"),
    questionType: $("#question-type"),
    topicLabel: $("#topic-label"),
    questionText: $("#question-text"),
    choiceList: $("#choice-list"),
    questionFigure: $("#question-figure"),
    questionImage: $("#question-image"),
    imageCaption: $("#image-caption"),
    answerText: $("#answer-text"),
    explanationText: $("#explanation-text"),
    previousButton: $("#previous-button"),
    nextButton: $("#next-button"),
    masterButton: $("#master-button"),
    shuffleButton: $("#shuffle-button"),
    progressBar: $("#progress-bar"),
    resetProgress: $("#reset-progress"),
    totalCardCount: $("#total-card-count"),
    moduleCount: $("#module-count"),
    masteredCount: $("#mastered-count"),
  };

  const activeModule = () => modules.find((module) => module.id === state.moduleId);

  function filteredCards() {
    const query = state.search.trim().toLowerCase();
    let cards = activeModule().cards.filter((card) => {
      const topicMatch = state.topic === "all" || card.topic === state.topic;
      const text = `${card.question} ${card.explanation} ${card.topic}`.toLowerCase();
      return topicMatch && (!query || text.includes(query));
    });
    if (state.shuffled) {
      const positions = new Map(state.shuffleOrder.map((id, index) => [id, index]));
      cards = cards.slice().sort((a, b) => (positions.get(a.id) ?? 9999) - (positions.get(b.id) ?? 9999));
    }
    return cards;
  }

  function saveMastered() {
    localStorage.setItem(storageKey, JSON.stringify([...state.mastered]));
  }

  function renderModuleNav() {
    elements.moduleNav.replaceChildren();
    modules.forEach((module) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `module-button${module.id === state.moduleId ? " active" : ""}`;
      button.innerHTML = `<strong>${module.label}</strong><span>${module.title}</span><small>${module.cards.length} cards</small>`;
      button.addEventListener("click", () => selectModule(module.id));
      elements.moduleNav.append(button);
    });
  }

  function renderTopics() {
    const topics = [...new Set(activeModule().cards.map((card) => card.topic))];
    elements.topicFilter.replaceChildren(new Option("All topics", "all"));
    topics.forEach((topic) => elements.topicFilter.add(new Option(topic, topic)));
    elements.topicFilter.value = state.topic;
  }

  function renderStats() {
    elements.totalCardCount.textContent = modules.reduce((sum, module) => sum + module.cards.length, 0);
    elements.moduleCount.textContent = String(modules.length).padStart(2, "0");
    elements.masteredCount.textContent = state.mastered.size;
  }

  function renderCard() {
    const module = activeModule();
    const cards = filteredCards();
    const hasCards = cards.length > 0;
    state.index = hasCards ? Math.min(state.index, cards.length - 1) : 0;
    document.documentElement.style.setProperty("--accent", module.accent);
    elements.deckKicker.textContent = module.label.toUpperCase();
    elements.deckTitle.textContent = module.title;
    elements.currentPosition.textContent = hasCards ? String(state.index + 1).padStart(2, "0") : "00";
    elements.filteredCount.textContent = String(cards.length).padStart(2, "0");
    elements.progressBar.style.width = hasCards ? `${((state.index + 1) / cards.length) * 100}%` : "0";
    elements.flashcard.hidden = !hasCards;
    elements.emptyState.hidden = hasCards;
    if (!hasCards) return;

    const card = cards[state.index];
    elements.flashcard.classList.remove("flipped");
    elements.questionLabel.textContent = `QUESTION ${String(card.number).padStart(2, "0")}`;
    elements.backQuestionLabel.textContent = `Q${String(card.number).padStart(2, "0")}`;
    elements.questionType.textContent = card.type;
    elements.topicLabel.textContent = card.topic;
    elements.questionText.textContent = card.question;
    elements.choiceList.replaceChildren();
    card.choices.forEach((choice) => {
      const item = document.createElement("li");
      item.dataset.label = choice.label;
      item.textContent = choice.text;
      elements.choiceList.append(item);
    });
    elements.answerText.textContent = formatAnswer(card);
    elements.explanationText.textContent = card.explanation;
    elements.questionFigure.hidden = !card.image;
    if (card.image) {
      elements.questionImage.src = card.image;
      elements.questionImage.alt = card.imageAlt || "Question diagram";
      elements.imageCaption.textContent = card.imageAlt || "Question diagram";
    } else {
      elements.questionImage.removeAttribute("src");
      elements.questionImage.alt = "";
      elements.imageCaption.textContent = "";
    }
    const mastered = state.mastered.has(card.id);
    elements.masterButton.classList.toggle("mastered", mastered);
    elements.masterButton.innerHTML = mastered ? '<span aria-hidden="true">✓</span> Mastered' : '<span aria-hidden="true">✓</span> Mark mastered';
    renderStats();
  }

  function formatAnswer(card) {
    const choice = card.choices.find((item) => item.label === card.answer);
    return choice ? `${card.answer}. ${choice.text}` : card.answer;
  }

  function selectModule(moduleId) {
    state.moduleId = moduleId;
    state.index = 0;
    state.search = "";
    state.topic = "all";
    state.shuffled = false;
    elements.searchInput.value = "";
    renderModuleNav();
    renderTopics();
    renderCard();
  }

  function move(delta) {
    const cards = filteredCards();
    if (!cards.length) return;
    state.index = (state.index + delta + cards.length) % cards.length;
    renderCard();
  }

  function toggleMastered() {
    const card = filteredCards()[state.index];
    if (!card) return;
    state.mastered.has(card.id) ? state.mastered.delete(card.id) : state.mastered.add(card.id);
    saveMastered();
    renderCard();
  }

  elements.flashcard.addEventListener("click", () => elements.flashcard.classList.toggle("flipped"));
  elements.previousButton.addEventListener("click", () => move(-1));
  elements.nextButton.addEventListener("click", () => move(1));
  elements.masterButton.addEventListener("click", toggleMastered);
  elements.searchInput.addEventListener("input", (event) => { state.search = event.target.value; state.index = 0; renderCard(); });
  elements.topicFilter.addEventListener("change", (event) => { state.topic = event.target.value; state.index = 0; renderCard(); });
  elements.shuffleButton.addEventListener("click", () => {
    state.shuffled = true;
    state.shuffleOrder = activeModule().cards.map((card) => card.id).sort(() => Math.random() - 0.5);
    state.index = 0;
    renderCard();
  });
  elements.resetProgress.addEventListener("click", () => {
    if (window.confirm("Clear all mastered-card progress?")) {
      state.mastered.clear();
      saveMastered();
      renderCard();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (["INPUT", "SELECT"].includes(document.activeElement.tagName)) return;
    if (event.code === "Space") { event.preventDefault(); elements.flashcard.classList.toggle("flipped"); }
    if (event.key === "ArrowLeft") move(-1);
    if (event.key === "ArrowRight") move(1);
    if (event.key.toLowerCase() === "m") toggleMastered();
  });

  renderModuleNav();
  renderTopics();
  renderStats();
  renderCard();
})();
