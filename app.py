import openai
import json
import os

# --- IMPORTANT PRE-REQUISITE ---
# This code requires the OpenAI Python library (`pip install openai`)
# and your OpenAI API key to be set as an environment variable named OPENAI_API_KEY.
# For example: export OPENAI_API_KEY='your_key_here'

def analyze_contract_with_ai(contract_text):
    """
    Analyzes contract text using OpenAI's API and returns a structured JSON object.
    """
    # This automatically picks up the API key from your environment variables
    client = openai.OpenAI()

    # The system prompt is the most critical part. It instructs the AI on its
    # role, the desired output format, and the exact criteria for the analysis.
    system_prompt = '''
You are ClauseSpy, a world-class legal AI assistant. Your task is to analyze a given contract and provide a structured JSON output. Do not output any text other than the JSON object itself.

The JSON object must have the following structure:
{
  "overall_risk": "Low/Medium/High",
  "plain_summary": "A brief, one-sentence status like 'Ready to Read' or 'Requires Attention'.",
  "opportunities_found": an integer count of positive clauses or opportunities,
  "risk_breakdown": [
    {
      "risk_level": "Low/Medium/High/Opportunity",
      "title": "A short, descriptive title for the clause (e.g., 'Unlimited Liability').",
      "description": "A clear, concise explanation of the clause, its risks or benefits, and a recommended action if applicable."
    }
  ]
}

Analyze all aspects of the contract: risks (from high to low), exit causes, payment terms, liability, intellectual property, confidentiality, and any positive clauses or opportunities for the user. Be thorough and precise.
'''

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # Using a powerful model for better legal interpretation
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": contract_text}
            ],
            # This ensures the output is a valid JSON object
            response_format={"type": "json_object"}
        )

        # The API returns a JSON string, so we parse it into a Python dictionary
        analysis_result = json.loads(response.choices[0].message.content)
        return analysis_result

    except Exception as e:
        # In a real app, you would have more robust error handling and logging
        print(f"An error occurred: {e}")
        return None

# --- HOW TO USE IT ---

# 1. In your web application backend, after a user uploads a PDF,
#    you'll first need a library (like PyMuPDF or pdfplumber) to extract the raw text.
#    For example:
#    extracted_text = extract_text_from_pdf("path/to/uploaded_contract.pdf")

# 2. For demonstration, we'll use a sample contract string here.
sample_contract = """
FREELANCE DESIGN AGREEMENT

This Agreement is made on November 12, 2025, between The Client and The Designer.

1. Scope of Work: The Designer will create a new company logo and brand guidelines.
2. Payment: The Client agrees to pay a total fee of $2,500. 50% is due upfront, and the remaining 50% is due upon final delivery.
3. Liability: The Designer's liability for any and all damages shall not, under any circumstances, exceed the total fee paid under this agreement.
4. Term and Termination: This agreement will automatically renew on an annual basis unless a 90-day written notice is provided by either party.
5. Confidentiality: Both parties agree to maintain the confidentiality of all proprietary information shared during the project.
6. Force Majeure: Neither party shall be held liable for any failure to perform its obligations where such failure is due to unforeseen circumstances beyond its reasonable control, such as acts of God, war, or natural disasters.
7. Opportunities: Based on the performance of this project, the Client may offer the Designer a long-term retainer contract for ongoing design services.
"""

# 3. Call the analysis function with the extracted text.
#    (Note: This will fail here because no API key is set in this environment)
analysis_data = analyze_contract_with_ai(sample_contract)

# 4. This `analysis_data` is the JSON object you'll send to your front-end.
if analysis_
    print(json.dumps(analysis_data, indent=4))

