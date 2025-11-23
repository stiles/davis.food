#!/usr/bin/env python3
"""
Fetch and analyze Davis_Big_Dawg's school lunch reviews.

This script demonstrates how to use tiktools to:
1. Fetch all posts from a TikTok user
2. Extract transcripts from videos
3. Extract structured review data using OpenAI

Requirements:
    pip install tiktools openai

Environment variables:
    TIKAPI_KEY - Your TikAPI key from https://tikapi.io
    OPENAI_API_KEY - Your OpenAI API key (optional, for review extraction)

Usage:
    # Fetch posts and transcripts
    python fetch_archive.py
    
    # Also extract review data with OpenAI
    python fetch_archive.py --extract-reviews
    
    # Update mode (only fetch new content)
    python fetch_archive.py --update
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from tiktools import fetch_user_posts, extract_transcripts
except ImportError:
    print("Error: tiktools is not installed.")
    print("Install it with: pip install tiktools")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and analyze Davis_Big_Dawg's school lunch reviews"
    )
    parser.add_argument(
        "--username",
        default="davis_big_dawg",
        help="TikTok username to fetch (default: davis_big_dawg)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./data"),
        help="Base directory for output files (default: ./data)"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update mode: only fetch new posts and transcripts"
    )
    parser.add_argument(
        "--extract-reviews",
        action="store_true",
        help="Extract structured review data using OpenAI (requires OPENAI_API_KEY)"
    )
    parser.add_argument(
        "--skip-transcripts",
        action="store_true",
        help="Skip transcript extraction (only fetch posts)"
    )
    parser.add_argument(
        "--force-transcripts",
        action="store_true",
        help="Force re-download of transcripts even if they exist (USE WITH CAUTION: will overwrite manual edits)"
    )
    
    args = parser.parse_args()
    
    # Check for TikAPI key
    if not os.getenv('TIKAPI_KEY'):
        print("Error: TIKAPI_KEY environment variable not set")
        print("Get your API key from https://tikapi.io")
        print("\nSet it with:")
        print('  export TIKAPI_KEY="your_api_key_here"')
        sys.exit(1)
    
    # Set up paths
    username = args.username
    user_dir = args.output_dir / username
    posts_file = user_dir / f"{username}_posts.json"
    transcripts_dir = user_dir / "transcripts"
    transcripts_file = transcripts_dir / f"{username}_transcripts.json"
    reviews_file = user_dir / f"{username}_reviews.json"
    
    print("=" * 80)
    print(f"DAVIS BIG DAWG ARCHIVE FETCHER")
    print("=" * 80)
    print(f"Username: @{username}")
    print(f"Output directory: {user_dir}")
    print(f"Update mode: {'Yes' if args.update else 'No'}")
    print()
    
    # Step 1: Fetch posts
    print("STEP 1: Fetching posts")
    print("-" * 80)
    
    try:
        posts_data = fetch_user_posts(
            username=username,
            output_file=posts_file,
            update_mode=args.update
        )
        
        print(f"\nFetched {posts_data['fetched_count']} posts")
        if args.update and 'new_posts' in posts_data:
            print(f"New posts: {posts_data['new_posts']}")
        print(f"Saved to: {posts_file}")
        
    except Exception as e:
        print(f"Error fetching posts: {e}")
        sys.exit(1)
    
    # Step 2: Extract transcripts
    if not args.skip_transcripts:
        print("\n" + "=" * 80)
        print("STEP 2: Extracting transcripts")
        print("-" * 80)
        
        # Protect existing transcripts unless --force-transcripts is used
        skip_existing = not args.force_transcripts
        if skip_existing:
            print("Note: Existing transcript files will be preserved (use --force-transcripts to override)")
        else:
            print("WARNING: --force-transcripts enabled - existing transcripts may be overwritten!")
        
        try:
            results = extract_transcripts(
                posts_file=posts_file,
                output_format="both",  # Save individual files and combined JSON
                language="eng",
                update_mode=args.update,
                skip_existing=skip_existing  # Protect manually edited transcripts
            )
            
            print("\nTranscript extraction complete:")
            print(f"  Total posts: {results['total_posts']}")
            print(f"  Transcripts found: {results['transcripts_found']}")
            print(f"  Transcripts downloaded: {results['transcripts_downloaded']}")
            print(f"  Failed: {results['failed']}")
            
            if args.update and results.get('skipped_existing', 0) > 0:
                print(f"  Skipped (already processed): {results['skipped_existing']}")
            
            print(f"\nSaved to: {transcripts_dir}/")
            
            # Show some stats
            if results['transcripts']:
                original_audio = sum(
                    1 for t in results['transcripts'] 
                    if t.get('is_original_audio', False)
                )
                print(f"\nAudio statistics:")
                print(f"  Original audio: {original_audio}")
                print(f"  Non-original audio: {len(results['transcripts']) - original_audio}")
                print(f"  (Non-original may contain song lyrics instead of speech)")
            
        except Exception as e:
            print(f"Error extracting transcripts: {e}")
            sys.exit(1)
    
    # Step 3: Extract review data (optional)
    if args.extract_reviews:
        print("\n" + "=" * 80)
        print("STEP 3: Extracting structured review data")
        print("-" * 80)
        
        # Check for OpenAI key
        if not os.getenv('OPENAI_API_KEY'):
            print("Error: OPENAI_API_KEY environment variable not set")
            print("Get your API key from https://platform.openai.com/api-keys")
            print("\nSet it with:")
            print('  export OPENAI_API_KEY="your_api_key_here"')
            print("\nSkipping review extraction...")
        else:
            try:
                # Import the extract_reviews script from the same directory
                script_dir = Path(__file__).parent
                sys.path.insert(0, str(script_dir))
                from extract_reviews import process_transcripts
                
                review_results = process_transcripts(
                    transcripts_json=str(transcripts_file),
                    update_mode=args.update,
                    existing_reviews_file=reviews_file if args.update else None
                )
                
                print(f"\nReview extraction complete:")
                print(f"  School food reviews: {review_results['school_food_reviews']}")
                print(f"  Other content: {review_results['other_content']}")
                print(f"  Failed: {review_results['failed']}")
                print(f"  Needs manual review: {review_results['needs_manual_review']}")
                print(f"\nSaved to: {reviews_file}")
                
            except ImportError:
                print("Error: extract_reviews.py not found in current directory")
                print("Make sure you're running this from examples/food_reviews/")
            except Exception as e:
                print(f"Error extracting reviews: {e}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("COMPLETE!")
    print("=" * 80)
    print(f"\nYour Davis Big Dawg archive is ready:")
    print(f"  Posts: {posts_file}")
    if not args.skip_transcripts:
        print(f"  Transcripts: {transcripts_dir}/")
    if args.extract_reviews and os.getenv('OPENAI_API_KEY'):
        print(f"  Reviews: {reviews_file}")
    
    print("\nNext steps:")
    if not args.extract_reviews:
        print(f"  - Extract reviews: python {Path(__file__).name} --extract-reviews")
    if not args.skip_transcripts and transcripts_file.exists():
        print(f"  - Calculate stats: python calculate_stats.py {reviews_file}")
    print(f"  - Update archive: python {Path(__file__).name} --update")
    print()


if __name__ == "__main__":
    main()

