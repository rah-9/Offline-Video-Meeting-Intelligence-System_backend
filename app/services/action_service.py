from fastapi import Request
from app.utils.logger import logger

def extract_actions_and_decisions_sync(request: Request, chunks: list, job_id: str):
    logger.info(f"Extracting actions and decisions for job {job_id}")
    
    nlp = request.app.state.nlp
    action_items = []
    decisions = []
    
    action_keywords = ["need to", "must", "should", "will", "action item", "todo", "assigned to"]
    decision_keywords = ["decided", "decision", "agreed", "consensus"]
    
    for chunk in chunks:
        doc = nlp(chunk["text"])
        for sent in doc.sents:
            sent_str = sent.text.lower()
            
            # Simple rule-based extraction
            if any(kw in sent_str for kw in action_keywords):
                action_items.append({"text": sent.text.strip(), "assignee": None})
            
            if any(kw in sent_str for kw in decision_keywords):
                decisions.append({"text": sent.text.strip()})
                
    return action_items[:10], decisions[:10]
