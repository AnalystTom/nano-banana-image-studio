#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key configured: {bool(api_key)}")
print(f"API Key (first 10 chars): {api_key[:10] if api_key else 'None'}")

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        print("Client created successfully")

        # Try a simple video generation
        print("\nAttempting to generate video...")
        response = client.models.generate_content(
            model='veo-3.0-generate-preview',
            contents='A person walking on a beach at sunset',
            config={'response_modalities': ['VIDEO']}
        )

        print(f"Response type: {type(response)}")
        print(f"Response: {response}")

        if hasattr(response, 'candidates'):
            print(f"Candidates: {len(response.candidates)}")
            if response.candidates:
                candidate = response.candidates[0]
                print(f"Candidate content: {candidate.content}")
                if candidate.content and candidate.content.parts:
                    part = candidate.content.parts[0]
                    print(f"Part type: {type(part)}")
                    print(f"Part: {part}")
                    if hasattr(part, 'inline_data'):
                        print(f"Has inline_data: {part.inline_data is not None}")
                        if part.inline_data:
                            print(f"Data size: {len(part.inline_data.data)} bytes")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
