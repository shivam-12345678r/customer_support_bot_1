import logging
import random
import anthropic
import PyPDF2

# Setup logging
logging.basicConfig(filename='support_bot_log2.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
client = anthropic.Anthropic(api_key='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')  

class SupportBotAgent:
    """
    A customer support bot that trains on a provided document,
    answers queries using Claude-3 Opus, and improves responses based on feedback.
    """
    def __init__(self, document_path):
        logging.info("Initializing SupportBotAgent")
        self.client = anthropic.Anthropic(api_key='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')
        self.document_text = self.load_document(document_path)
        logging.info(f"Loaded document: {document_path}")

    def load_document(self, path):
        """Loads and extracts text from a document (TXT or PDF)."""
        try:
            if path.endswith('.pdf'):
                return self.extract_text_from_pdf(path)
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logging.error(f"Error loading document: {e}")
            return ""

    def extract_text_from_pdf(self, pdf_path):
        """Extracts text from a PDF file."""
        text = ""
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {e}")
        return text

    def answer_query(self, query):
        """Generates an answer using Claude-3 Opus."""
        prompt = f"""
        You are a customer support assistant. Answer the following query based on the provided document context:
        {self.document_text}
        
        Query: {query}
        """
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content
        except Exception as e:
            logging.error(f"Error getting response from Claude: {e}")
            return "I'm unable to process your request at the moment. Please try again later."

    def get_feedback(self, response):
        """Simulates feedback (or allows manual entry in the future)."""
        feedback = random.choice(["not helpful", "too vague", "good"])
        logging.info(f"Feedback received: {feedback}")
        return feedback

    def adjust_response(self, query, response, feedback):
        """Refines the response based on feedback."""
        if feedback == "too vague":
            return f"{response} (Additional context: {self.document_text[:100]}...)"
        elif feedback == "not helpful":
            return self.answer_query(query + " Please provide more details.")
        return response

    def run(self, queries):
        """Processes a list of queries and iterates based on feedback."""
        for query in queries:
            logging.info(f"Processing query: {query}")
            response = self.answer_query(query)
            print(f"Initial Response to '{query}': {response}")

            for _ in range(2):  # Feedback loop
                feedback = self.get_feedback(response)
                if feedback == "good":
                    break
                response = self.adjust_response(query, response, feedback)
                print(f"Updated Response to '{query}': {response}")

if __name__ == "__main__":
    bot = SupportBotAgent("faq.txt")  # Ensure faq.txt is in the same directory
    sample_queries = [
        "How do I reset my password?",
        "What’s the refund policy?",
        "How do I delete my account?"
    ]
    bot.run(sample_queries)

