from fastapi import Request
from app.utils.logger import logger

def summarize_text_sync(request: Request, text: str, max_length: int = 150, min_length: int = 50):
    summarizer = request.app.state.summarizer
    
    try:
        input_length = len(text.split())
        adjusted_max = min(max_length, max(int(input_length * 0.5), min_length + 10))
        
        res = summarizer(text[:4000], max_length=adjusted_max, min_length=min_length, do_sample=False)
        return res[0]['summary_text']
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        return text[:max_length]

def generate_hierarchical_summary_sync(request: Request, chunks: list, job_id: str):
    logger.info(f"Generating hierarchical summaries for job {job_id}")
    
    if not chunks:
        return "No content.", "No content."
        
    chunk_summaries = []
    for chunk in chunks:
        summary = summarize_text_sync(request, chunk["text"], max_length=150, min_length=40)
        chunk_summaries.append(summary)
        
    detailed_summary = "\n\n".join([f"- {s}" for s in chunk_summaries])
    
    # Final summary pass over combined chunk summaries
    combined_text = " ".join(chunk_summaries)
    short_summary = summarize_text_sync(request, combined_text, max_length=150, min_length=50)
    
    return short_summary, detailed_summary

def answer_question_sync(request: Request, question: str, context: str, history: list = None, is_general: bool = False):
    qa_pipeline = request.app.state.qa_pipeline
    try:
        if not context.strip() and not is_general:
            return "No relevant context found to answer the specific question."
            
        history_text = "\n".join([f"User: {h.get('q', '')}\nAssistant: {h.get('a', '')}" for h in (history or [])])
        history_block = f"Conversation History:\n{history_text}\n\n" if history_text else ""
        
        if is_general:
            prompt = (
                "Answer the following question using your general knowledge, or the provided background context if it is relevant. "
                "Keep the answer concise and direct.\n\n"
                f"{history_block}"
                f"Background:\n{context}\n\n"
                f"Q: {question}\n"
                "A:"
            )
        else:
            prompt = (
                "Answer the following question based ONLY on the provided Background and Conversation History. "
                "Do not use outside knowledge. If the answer cannot be found in the background, say 'I cannot answer this based on the provided context.'\n\n"
                f"{history_block}"
                f"Background:\n{context}\n\n"
                f"Q: {question}\n"
                "A:"
            )
            
        # Flan-T5 has an input length limit, truncate if necessary
        # We must strictly ensure the instructions and the final Question + "A:" blocks remain perfectly intact.
        if len(prompt) > 2500:
            prompt_start = prompt[:200]
            question_block = f"\n\nQ: {question}\nA:"
            
            # Calculate how much context we can actually keep safely
            allowed_context_len = 2500 - len(prompt_start) - len(question_block) - 5
            
            # Rebuild prompt with safe boundaries
            safe_context = context[:allowed_context_len] + "..."
            
            if is_general:
                prompt = f"{prompt_start}{history_block}Background:\n{safe_context}{question_block}"
            else:
                prompt = f"{prompt_start}{history_block}Background:\n{safe_context}{question_block}"
            
        result = qa_pipeline(prompt, max_length=200, do_sample=False, num_beams=3, early_stopping=True)
        answer = result[0]['generated_text']
        
        # FLAN-T5 sometimes outputs variants of its explicit inability clause. Catch them gracefully.
        if "I cannot answer this" in answer or "unanswerable" in answer.lower():
            if not is_general:
                return "I cannot find a specific answer to this in the meeting text."
        
        return answer
    except Exception as e:
        logger.error(f"Question Answering error: {e}")
        return "Sorry, an error occurred while searching to answer your question."
