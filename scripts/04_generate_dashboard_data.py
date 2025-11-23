#!/usr/bin/env python3
"""
Generate pre-computed dashboard data for davis.food website.

This script processes the reviews JSON and generates a comprehensive
dashboard_stats.json file with all metrics needed for the static site.

No API calls required - can be run anytime on existing data.
"""

import json
import re
from pathlib import Path
from typing import Dict, List
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo


def sentence_case(text: str) -> str:
    """Convert text to sentence case."""
    if not text:
        return text
    return text[0].upper() + text[1:].lower() if len(text) > 1 else text.upper()


def extract_key_phrases(reviews: List[Dict]) -> List[str]:
    """
    Extract Davis's characteristic phrases from food comments.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        List of unique key phrases in sentence case
    """
    phrases = []
    
    for review in reviews:
        for food in review.get('foods', []):
            comment = food.get('comments', '')
            if not comment:
                continue
                
            # Extract common Davis phrases
            # Look for sentences or short phrases
            sentences = re.split(r'[.!]', comment)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    # Keep phrases that are characteristic
                    lower = sentence.lower()
                    if any(keyword in lower for keyword in [
                        'pretty good', 'really good', 'super', 'very',
                        'not that great', 'kind of', 'actually',
                        'nice and', 'love', 'favorite', 'not the biggest',
                        'definitely', 'bland', 'soggy', 'dry', 'crisp'
                    ]):
                        phrases.append(sentence)
    
    # Get unique phrases, sorted by frequency, convert to sentence case
    phrase_counts = Counter(phrases)
    # Return top 30 most common phrases in sentence case
    return [sentence_case(phrase) for phrase, count in phrase_counts.most_common(30)]


def calculate_cumulative_stats(reviews: List[Dict]) -> List[Dict]:
    """
    Calculate cumulative engagement stats over time for charting.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        List of time series data points
    """
    # Sort reviews by date
    sorted_reviews = sorted(
        [r for r in reviews if r.get('create_time')],
        key=lambda x: x['create_time']
    )
    
    cumulative_data = []
    cum_likes = 0
    cum_views = 0
    cum_comments = 0
    cum_shares = 0
    
    for review in sorted_reviews:
        stats = review.get('stats', {})
        cum_likes += stats.get('diggCount', 0)
        cum_views += stats.get('playCount', 0)
        cum_comments += stats.get('commentCount', 0)
        cum_shares += stats.get('shareCount', 0)
        
        # Convert timestamp to ISO date string
        date = datetime.fromtimestamp(review['create_time']).strftime('%Y-%m-%d')
        
        cumulative_data.append({
            'date': date,
            'timestamp': review['create_time'],
            'day_number': review.get('day_number'),
            'cumulative_likes': cum_likes,
            'cumulative_views': cum_views,
            'cumulative_comments': cum_comments,
            'cumulative_shares': cum_shares
        })
    
    return cumulative_data


def calculate_category_stats(reviews: List[Dict]) -> Dict:
    """
    Calculate average ratings and counts by food category.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        Dictionary with category statistics
    """
    category_scores = {}
    
    for review in reviews:
        for food in review.get('foods', []):
            category = food.get('category', 'other')
            score = food.get('score')
            if score is not None:
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(score)
    
    category_stats = {}
    for category, scores in category_scores.items():
        category_stats[category] = {
            'average_rating': round(sum(scores) / len(scores), 2),
            'count': len(scores),
            'min': min(scores),
            'max': max(scores)
        }
    
    return category_stats


def format_number(num: int) -> str:
    """Format number for display (e.g., 1.2M, 543K)."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.0f}K"
    return str(num)


def get_top_posts(reviews: List[Dict], limit: int = 6) -> List[Dict]:
    """
    Get top posts by engagement score.
    
    Args:
        reviews: List of review dictionaries
        limit: Number of top posts to return
        
    Returns:
        List of top posts with relevant fields
    """
    posts_with_engagement = []
    
    for review in reviews:
        # Skip Texas Roadhouse post (not a school lunch review)
        description = review.get('description', '').lower()
        if 'texas roadhouse' in description or 'texasroadhouse' in description:
            continue
            
        stats = review.get('stats', {})
        engagement_score = (
            stats.get('diggCount', 0) +
            stats.get('commentCount', 0) +
            stats.get('shareCount', 0)
        )
        
        # Calculate average rating for the post
        foods = review.get('foods', [])
        scores = [f.get('score') for f in foods if f.get('score') is not None]
        avg_rating = round(sum(scores) / len(scores), 2) if scores else None
        
        post_id = review.get('post_id')
        
        posts_with_engagement.append({
            'post_id': post_id,
            'day_number': review.get('day_number'),
            'date': datetime.fromtimestamp(review['create_time']).strftime('%Y-%m-%d') if review.get('create_time') else None,
            'timestamp': review.get('create_time'),
            'engagement_score': engagement_score,
            'likes': stats.get('diggCount', 0),
            'likes_formatted': format_number(stats.get('diggCount', 0)),
            'views': stats.get('playCount', 0),
            'views_formatted': format_number(stats.get('playCount', 0)),
            'comments': stats.get('commentCount', 0),
            'comments_formatted': format_number(stats.get('commentCount', 0)),
            'shares': stats.get('shareCount', 0),
            'average_rating': avg_rating,
            'food_count': len(foods),
            'tiktok_url': f"https://www.tiktok.com/@davis_big_dawg/video/{post_id}" if post_id else None,
            'thumbnail_url': f"https://www.tiktok.com/@davis_big_dawg/video/{post_id}" if post_id else None
        })
    
    # Sort by engagement and return top N
    return sorted(posts_with_engagement, key=lambda x: x['engagement_score'], reverse=True)[:limit]


def prepare_posts_table(reviews: List[Dict]) -> List[Dict]:
    """
    Prepare all posts data for table display.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        List of posts with computed fields including accurate review_number
    """
    posts = []
    
    for review in reviews:
        # Skip Texas Roadhouse post
        description = review.get('description', '').lower()
        if 'texas roadhouse' in description or 'texasroadhouse' in description:
            continue
            
        stats = review.get('stats', {})
        foods = review.get('foods', [])
        scores = [f.get('score') for f in foods if f.get('score') is not None]
        avg_rating = round(sum(scores) / len(scores), 2) if scores else None
        
        post_id = review.get('post_id')
        
        # Prepare foods list with details
        foods_list = []
        for food in foods:
            if food.get('name'):
                # Sentence case the food name
                name = food.get('name', '')
                sentence_cased_name = name[0].upper() + name[1:] if name else name
                foods_list.append({
                    'name': sentence_cased_name,
                    'score': food.get('score'),
                    'category': food.get('category', 'unknown')
                })
        
        posts.append({
            'post_id': post_id,
            'day_number': review.get('day_number'),
            'date': datetime.fromtimestamp(review['create_time']).strftime('%Y-%m-%d') if review.get('create_time') else None,
            'timestamp': review.get('create_time'),
            'average_rating': avg_rating,
            'food_count': len(foods),
            'foods': foods_list,
            'likes': stats.get('diggCount', 0),
            'views': stats.get('playCount', 0),
            'comments': stats.get('commentCount', 0),
            'shares': stats.get('shareCount', 0),
            'tiktok_url': f"https://www.tiktok.com/@davis_big_dawg/video/{post_id}" if post_id else None,
            'needs_review': review.get('needs_review', False)
        })
    
    # Sort by date ascending to assign review numbers
    posts.sort(key=lambda x: x['timestamp'] or 0)
    
    # Assign accurate review_number based on chronological order
    # Number ALL reviews sequentially starting at 1
    for i, post in enumerate(posts, start=1):
        post['review_number'] = i
    
    # Sort by date descending (most recent first) for display
    return sorted(posts, key=lambda x: x['timestamp'] or 0, reverse=True)


def calculate_food_frequency(reviews: List[Dict], limit: int = 10) -> List[Dict]:
    """
    Calculate frequency of different foods across all reviews.
    
    Args:
        reviews: List of review dictionaries
        limit: Number of top foods to return
        
    Returns:
        List of foods with their frequency counts
    """
    food_counts = Counter()
    
    for review in reviews:
        for food in review.get('foods', []):
            # Normalize food names
            name = food.get('name', '').lower().strip()
            if name and name != 'unknown food':
                food_counts[name] += 1
    
    # Get top N foods
    top_foods = []
    for name, count in food_counts.most_common(limit):
        # Capitalize each word
        display_name = ' '.join(word.capitalize() for word in name.split())
        top_foods.append({
            'name': display_name,
            'count': count
        })
    
    return top_foods


def calculate_overall_metrics(reviews: List[Dict]) -> Dict:
    """
    Calculate overall dashboard metrics.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        Dictionary with overall metrics
    """
    # Count school food reviews (exclude Texas Roadhouse and other non-school posts)
    school_reviews = []
    for r in reviews:
        description = r.get('description', '').lower()
        if 'texas roadhouse' not in description and 'texasroadhouse' not in description:
            school_reviews.append(r)
    
    # Count all food items
    all_foods = []
    for review in reviews:
        all_foods.extend(review.get('foods', []))
    
    # Calculate overall average rating
    all_scores = [f.get('score') for f in all_foods if f.get('score') is not None]
    overall_avg = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0
    
    # Count by category
    category_counts = Counter()
    for food in all_foods:
        category = food.get('category', 'other')
        category_counts[category] += 1
    
    # Find favorite category (highest average)
    category_stats = calculate_category_stats(reviews)
    favorite_category = None
    if category_stats:
        favorite_category = max(
            category_stats.items(),
            key=lambda x: x[1]['average_rating']
        )[0]
    
    return {
        'total_reviews': len(reviews),
        'school_lunch_reviews': len(school_reviews),
        'total_food_items': len(all_foods),
        'overall_average_rating': overall_avg,
        'favorite_category': favorite_category,
        'category_counts': dict(category_counts)
    }


def get_latest_review(reviews: List[Dict], posts_data: Dict) -> Dict:
    """
    Get the latest review with full details including thumbnail.
    
    Args:
        reviews: List of review dictionaries
        posts_data: Posts JSON data with metadata
        
    Returns:
        Dictionary with latest review data
    """
    # Filter out Texas Roadhouse
    filtered_reviews = [r for r in reviews if r.get('post_id') != '7556759729863724301']
    
    if not filtered_reviews:
        return {}
    
    # Sort by timestamp (most recent first)  
    sorted_reviews = sorted(
        filtered_reviews,
        key=lambda x: x.get('create_time', 0),
        reverse=True
    )
    
    # Calculate review number (chronological order)
    chronological_reviews = sorted(
        filtered_reviews,
        key=lambda x: x.get('create_time', 0)
    )
    
    latest = sorted_reviews[0]
    post_id = latest.get('post_id')
    
    # Find review number (1-indexed chronological position)
    review_number = next(
        (i + 1 for i, r in enumerate(chronological_reviews) if r.get('post_id') == post_id),
        None
    )
    
    # Find matching post for thumbnail and stats
    thumbnail_url = None
    tiktok_url = f"https://www.tiktok.com/@davis_big_dawg/video/{post_id}"
    engagement = {
        'likes': 0,
        'comments': 0,
        'shares': 0,
        'views': 0,
        'likes_formatted': '0',
        'comments_formatted': '0',
        'shares_formatted': '0',
        'views_formatted': '0'
    }
    
    for post in posts_data.get('posts', []):
        if post.get('id') == post_id:
            # Get cover image
            video_data = post.get('video', {})
            cover = video_data.get('cover', '')
            if not cover:
                # Try cover field directly
                cover = video_data.get('dynamicCover', '')
            thumbnail_url = cover
            
            # Get engagement stats
            stats = post.get('stats', {})
            engagement = {
                'likes': stats.get('diggCount', 0),
                'comments': stats.get('commentCount', 0),
                'shares': stats.get('shareCount', 0),
                'views': stats.get('playCount', 0),
                'likes_formatted': format_number(stats.get('diggCount', 0)),
                'comments_formatted': format_number(stats.get('commentCount', 0)),
                'shares_formatted': format_number(stats.get('shareCount', 0)),
                'views_formatted': format_number(stats.get('playCount', 0))
            }
            break
    
    # Calculate average rating
    foods = latest.get('foods', [])
    if foods:
        avg_rating = sum(f.get('score', 0) for f in foods) / len(foods)
    else:
        avg_rating = 0
    
    # Sentence case food names
    for food in foods:
        food['name'] = sentence_case(food.get('name', ''))
    
    # Get create time for date comparison
    create_time = latest.get('create_time', 0)
    if create_time:
        from datetime import datetime
        post_date = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d')
    else:
        post_date = latest.get('date', '')
    
    return {
        'post_id': post_id,
        'day_number': latest.get('day_number'),
        'review_number': review_number,
        'date': post_date,
        'foods': foods,
        'average_rating': round(avg_rating, 1),
        'thumbnail_url': thumbnail_url,
        'tiktok_url': tiktok_url,
        'engagement': engagement
    }


def generate_dashboard_data(reviews_json_path: Path, output_path: Path):
    """
    Generate comprehensive dashboard data file.
    
    Args:
        reviews_json_path: Path to reviews JSON file
        output_path: Path to output dashboard stats JSON
    """
    print(f"Loading reviews from {reviews_json_path}...")
    
    with open(reviews_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    username = data.get('username', 'unknown')
    reviews = data.get('reviews', [])
    
    # Load posts data for thumbnails
    posts_json_path = reviews_json_path.parent / f"{username}_posts.json"
    print(f"Loading posts from {posts_json_path}...")
    
    with open(posts_json_path, 'r', encoding='utf-8') as f:
        posts_data = json.load(f)
    
    print(f"Processing {len(reviews)} reviews for @{username}...")
    
    # Generate all dashboard data
    print("  - Calculating overall metrics...")
    overall_metrics = calculate_overall_metrics(reviews)
    
    print("  - Calculating category statistics...")
    category_stats = calculate_category_stats(reviews)
    
    print("  - Generating time series data...")
    time_series = calculate_cumulative_stats(reviews)
    
    print("  - Finding top posts...")
    top_posts = get_top_posts(reviews, limit=6)
    
    print("  - Extracting key phrases...")
    key_phrases = extract_key_phrases(reviews)
    
    print("  - Preparing posts table...")
    posts_table = prepare_posts_table(reviews)
    
    print("  - Calculating food frequency...")
    food_frequency = calculate_food_frequency(reviews, limit=10)
    
    print("  - Getting latest review...")
    latest_review = get_latest_review(reviews, posts_data)
    
    # Generate Pacific Time timestamp in desired format
    pacific_tz = ZoneInfo('America/Los_Angeles')
    now_pt = datetime.now(pacific_tz)
    
    # Format: "Nov. 23, 2025, at 8 a.m. PT"
    month = now_pt.strftime('%b')
    day = now_pt.day
    year = now_pt.year
    hour = now_pt.hour
    
    # Format hour as "8 a.m." or "2 p.m."
    if hour == 0:
        time_str = "12 a.m."
    elif hour < 12:
        time_str = f"{hour} a.m."
    elif hour == 12:
        time_str = "12 p.m."
    else:
        time_str = f"{hour - 12} p.m."
    
    generated_at_formatted = f"{month}. {day}, {year}, at {time_str} PT"
    
    # Compile dashboard data
    dashboard_data = {
        'generated_at': now_pt.isoformat(),  # Keep ISO format for machine parsing
        'generated_at_formatted': generated_at_formatted,  # Human-readable PT format
        'username': username,
        'overall_metrics': overall_metrics,
        'category_stats': category_stats,
        'time_series': time_series,
        'top_posts': top_posts,
        'key_phrases': key_phrases,
        'posts_table': posts_table,
        'food_frequency': food_frequency,
        'latest_review': latest_review
    }
    
    # Save to file
    print(f"\nSaving dashboard data to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    
    print("\nDashboard data generated successfully!")
    print(f"  Total reviews: {overall_metrics['total_reviews']}")
    print(f"  School lunch reviews: {overall_metrics['school_lunch_reviews']}")
    print(f"  Total food items: {overall_metrics['total_food_items']}")
    print(f"  Overall average rating: {overall_metrics['overall_average_rating']}/10")
    print(f"  Key phrases extracted: {len(key_phrases)}")
    print(f"  Time series data points: {len(time_series)}")


def main():
    """Command-line interface for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate dashboard data from TikTok review data"
    )
    parser.add_argument(
        "--reviews-json",
        type=Path,
        default=Path("data/davis_big_dawg/davis_big_dawg_reviews.json"),
        help="Path to reviews JSON file"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("data/dashboard_stats.json"),
        help="Output path for dashboard stats JSON"
    )
    
    args = parser.parse_args()
    
    try:
        if not args.reviews_json.exists():
            raise FileNotFoundError(f"Reviews file not found: {args.reviews_json}")
        
        generate_dashboard_data(args.reviews_json, args.output)
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

