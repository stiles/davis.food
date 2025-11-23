module.exports = function(eleventyConfig) {
  // Pass through assets
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/js");
  eleventyConfig.addPassthroughCopy("CNAME");
  
  // Pass through data directory for access to dashboard_stats.json
  eleventyConfig.addPassthroughCopy("data");
  
  // Add a filter to format dates
  eleventyConfig.addFilter("readableDate", (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  });
  
  // Add a filter to format numbers with commas
  eleventyConfig.addFilter("numberFormat", (num) => {
    if (num === null || num === undefined) return '0';
    return num.toLocaleString('en-US');
  });
  
  // Add a filter to format ratings
  eleventyConfig.addFilter("ratingFormat", (rating) => {
    if (rating === null || rating === undefined) return 'N/A';
    return rating.toFixed(1);
  });
  
  // Add a filter to format category names
  eleventyConfig.addFilter("categoryFormat", (category) => {
    if (!category) return 'N/A';
    // Replace underscores with hyphens and capitalize
    return category.replace(/_/g, '-').replace(/\b\w/g, l => l.toUpperCase());
  });
  
  // Add a filter to format large numbers as K/M
  eleventyConfig.addFilter("shortNumber", (num) => {
    if (num === null || num === undefined) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
    return num.toString();
  });
  
  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data"
    },
    templateFormats: ["njk", "html", "md"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};

