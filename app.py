def run_pipeline(question=None, article_text=None):
    """
    Campbell Fact Cognitive Pipeline
    Supports:
    - Question-only reasoning
    - Article-only fact extraction
    - Question + article comparative analysis
    """

    question = (question or "").strip()
    article_text = (article_text or "").strip()

    # --- MODE 1: Question Only ---
    if question and not article_text:
        return knowledge_mode(question)

    # --- MODE 2: Article Only ---
    elif article_text and not question:
        return article_extraction_mode(article_text)

    # --- MODE 3: Combined Mode ---
    elif question and article_text:
        return comparative_mode(question, article_text)

    # --- No Input ---
    else:
        return {
            "status": "error",
            "message": "Provide a question, an article, or both."
        }


# ---------- MODE IMPLEMENTATIONS ----------

def knowledge_mode(question):
    return {
        "mode": "question_only",
        "analysis": f"Running general knowledge reasoning for: {question}"
    }


def article_extraction_mode(article_text):
    return {
        "mode": "article_only",
        "analysis": "Extracting facts from provided article.",
        "length": len(article_text)
    }


def comparative_mode(question, article_text):
    return {
        "mode": "comparison",
        "analysis": f"Comparing article claims against question: {question}",
        "article_length": len(article_text)
    }
