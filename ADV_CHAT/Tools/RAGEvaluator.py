import time
from typing import List, Dict

class RAGEvaluator:
    def __init__(self):
        self.responses: List[Dict] = []

    def evaluate_response(self, query: str, response: str, context: List[Dict]) -> Dict:
        # Basic metrics: response length, citation count, and a simple relevance score.
        try:
            start_time = time.time()
            metrics = {
                'response_length': len(response),
                'source_citations': sum(1 for doc in context if doc["content"] in response),
                'evaluation_time': time.time() - start_time,
                'context_relevance': self._calculate_relevance(query, context)
            }
            self.responses.append({
                'query': query,
                'response': response,
                'metrics': metrics
            })
            return metrics
        except Exception as e:
            print(f"Error evaluating response: {e}")
            return None



    def _calculate_relevance(self, query: str, context: List[Dict]) -> float:
        # Simple relevance score: fraction of the documents where the query appears.
        return sum(1 for c in context if query.lower() in c["content"].lower()) / len(context)