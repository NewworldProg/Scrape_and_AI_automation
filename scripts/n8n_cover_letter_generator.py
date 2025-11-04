#!/usr/bin/env python3
"""
n8n Cover Letter Generator Script
Uses existing CoverLetterGenerator class with local AI and OpenAI providers
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai.cover_letter_generator import CoverLetterGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate cover letters using existing CoverLetterGenerator")
    parser.add_argument("--job_title", required=True, help="Job title")
    parser.add_argument("--job_description", required=True, help="Job description")
    parser.add_argument("--company", default="", help="Company name")
    parser.add_argument("--skills", default="", help="Comma-separated skills")
    parser.add_argument("--provider", default="local_ai", choices=["local_ai", "openai"], help="AI provider to use")
    parser.add_argument("--output_format", default="json", choices=["text", "json"], help="Output format")
    parser.add_argument("--max_words", type=int, default=200, help="Maximum words in cover letter")
    
    args = parser.parse_args()
    
    try:
        # Initialize the cover letter generator
        generator = CoverLetterGenerator(preferred_provider=args.provider)
        
        # Prepare job data
        skills_list = [skill.strip() for skill in args.skills.split(',') if skill.strip()] if args.skills else []
        
        job_data = {
            "title": args.job_title,
            "company": args.company or "the company",
            "description": args.job_description,
            "skills": skills_list
        }
        
        # Check available providers
        available_providers = generator.get_available_providers()
        
        # Generate cover letter
        cover_letter = generator.generate_cover_letter(job_data, provider=args.provider)
        
        # Limit word count if specified
        if args.max_words:
            words = cover_letter.split()
            if len(words) > args.max_words:
                cover_letter = " ".join(words[:args.max_words])
                # Try to end at a sentence
                if not cover_letter.endswith('.'):
                    last_period = cover_letter.rfind('.')
                    if last_period > len(cover_letter) * 0.8:
                        cover_letter = cover_letter[:last_period + 1]
                    else:
                        cover_letter += "."
        
        # Output result
        if args.output_format == "json":
            result = {
                "success": True,
                "cover_letter": cover_letter,
                "job_title": args.job_title,
                "company": args.company,
                "provider_used": args.provider,
                "available_providers": available_providers,
                "word_count": len(cover_letter.split()),
                "timestamp": datetime.now().isoformat()
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(cover_letter)
            
    except Exception as e:
        if args.output_format == "json":
            error_result = {
                "success": False,
                "error": str(e),
                "provider_used": args.provider,
                "timestamp": datetime.now().isoformat()
            }
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()