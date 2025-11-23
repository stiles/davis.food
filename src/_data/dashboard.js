const fs = require('fs');
const path = require('path');

module.exports = function() {
  // Load the pre-computed dashboard stats
  const dataPath = path.join(__dirname, '../../data/dashboard_stats.json');
  
  try {
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    return JSON.parse(rawData);
  } catch (error) {
    console.error('Error loading dashboard data:', error);
    // Return empty data structure if file doesn't exist
    return {
      generated_at: new Date().toISOString(),
      username: 'davis_big_dawg',
      overall_metrics: {
        total_reviews: 0,
        school_lunch_reviews: 0,
        total_food_items: 0,
        overall_average_rating: 0,
        favorite_category: null,
        category_counts: {}
      },
      category_stats: {},
      time_series: [],
      top_posts: [],
      key_phrases: [],
      posts_table: []
    };
  }
};

