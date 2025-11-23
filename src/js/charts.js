// D3.js Charts for davis.food dashboard

document.addEventListener('DOMContentLoaded', () => {
  if (typeof d3 === 'undefined') {
    console.error('D3.js not loaded');
    return;
  }
  
  if (!window.dashboardData) {
    console.error('Dashboard data not available');
    return;
  }
  
  // Initialize charts
  createViewsChart();
  createLikesChart();
  createCategoryChart();
  createFoodFrequencyChart();
  
  // Add table interactivity
  initializeTableFunctionality();
});

function createViewsChart() {
  const data = window.dashboardData.timeSeries;
  if (!data || data.length === 0) return;
  
  const container = document.getElementById('views-chart');
  const margin = {top: 20, right: 20, bottom: 40, left: 70};
  const width = container.offsetWidth - margin.left - margin.right;
  const height = 350 - margin.top - margin.bottom;
  
  const svg = d3.select('#views-chart')
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);
  
  data.forEach(d => d.date = new Date(d.date));
  
  const x = d3.scaleTime()
    .domain(d3.extent(data, d => d.date))
    .range([0, width]);
  
  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.cumulative_views)])
    .range([height, 0]);
  
  // Area
  const area = d3.area()
    .x(d => x(d.date))
    .y0(height)
    .y1(d => y(d.cumulative_views))
    .curve(d3.curveMonotoneX);
  
  svg.append('path')
    .datum(data)
    .attr('fill', 'rgba(0, 242, 234, 0.2)')
    .attr('d', area);
  
  // Line
  const line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.cumulative_views))
    .curve(d3.curveMonotoneX);
  
  svg.append('path')
    .datum(data)
    .attr('fill', 'none')
    .attr('stroke', '#00f2ea')
    .attr('stroke-width', 2)
    .attr('d', line);
  
  // Axes
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(4))
    .attr('class', 'axis');
  
  svg.append('g')
    .call(d3.axisLeft(y).ticks(5).tickFormat(d => {
      if (d >= 1000000) return (d / 1000000) + 'M';
      if (d >= 1000) return (d / 1000) + 'K';
      return d;
    }))
    .attr('class', 'axis');
  
  svg.selectAll('.domain, .tick line').remove();
}

function createLikesChart() {
  const data = window.dashboardData.timeSeries;
  if (!data || data.length === 0) return;
  
  const container = document.getElementById('likes-chart');
  const margin = {top: 20, right: 20, bottom: 40, left: 70};
  const width = container.offsetWidth - margin.left - margin.right;
  const height = 350 - margin.top - margin.bottom;
  
  const svg = d3.select('#likes-chart')
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);
  
  data.forEach(d => d.date = new Date(d.date));
  
  const x = d3.scaleTime()
    .domain(d3.extent(data, d => d.date))
    .range([0, width]);
  
  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.cumulative_likes)])
    .range([height, 0]);
  
  // Area
  const area = d3.area()
    .x(d => x(d.date))
    .y0(height)
    .y1(d => y(d.cumulative_likes))
    .curve(d3.curveMonotoneX);
  
  svg.append('path')
    .datum(data)
    .attr('fill', 'rgba(255, 0, 80, 0.2)')
    .attr('d', area);
  
  // Line
  const line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.cumulative_likes))
    .curve(d3.curveMonotoneX);
  
  svg.append('path')
    .datum(data)
    .attr('fill', 'none')
    .attr('stroke', '#ff0050')
    .attr('stroke-width', 2)
    .attr('d', line);
  
  // Axes
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(4))
    .attr('class', 'axis');
  
  svg.append('g')
    .call(d3.axisLeft(y).ticks(5).tickFormat(d => {
      if (d >= 1000000) return (d / 1000000) + 'M';
      if (d >= 1000) return (d / 1000) + 'K';
      return d;
    }))
    .attr('class', 'axis');
  
  svg.selectAll('.domain, .tick line').remove();
}

function createCategoryChart() {
  const data = window.dashboardData.categoryStats;
  if (!data || Object.keys(data).length === 0) return;
  
  const categoryArray = Object.entries(data)
    .map(([name, stats]) => {
      // Convert to sentence case: capitalize first letter only
      const readable = name.replace(/_/g, ' ');
      const sentenceCase = readable.charAt(0).toUpperCase() + readable.slice(1).toLowerCase();
      return {
        name: sentenceCase,
        rating: stats.average_rating,
        count: stats.count
      };
    })
    .sort((a, b) => b.rating - a.rating);
  
  const container = document.getElementById('category-chart');
  const margin = {top: 10, right: 60, bottom: 30, left: 100};
  const width = container.offsetWidth - margin.left - margin.right;
  const height = Math.max(300, categoryArray.length * 50) - margin.top - margin.bottom;
  
  const svg = d3.select('#category-chart')
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);
  
  const y = d3.scaleBand()
    .range([0, height])
    .domain(categoryArray.map(d => d.name))
    .padding(0.3);
  
  const x = d3.scaleLinear()
    .domain([0, 10])
    .range([0, width]);
  
  const color = d3.scaleLinear()
    .domain([0, 10])
    .range(['#ffcdd2', '#ff0050']);
  
  svg.selectAll('rect')
    .data(categoryArray)
    .enter()
    .append('rect')
    .attr('y', d => y(d.name))
    .attr('x', 0)
    .attr('height', y.bandwidth())
    .attr('width', d => x(d.rating))
    .attr('fill', d => color(d.rating))
    .attr('rx', 3);
  
  svg.selectAll('.label')
    .data(categoryArray)
    .enter()
    .append('text')
    .attr('y', d => y(d.name) + y.bandwidth() / 2)
    .attr('x', d => x(d.rating) + 5)
    .attr('dy', '0.35em')
    .style('font-size', '11px')
    .style('font-weight', '700')
    .style('fill', '#161823')
    .text(d => `${d.rating.toFixed(1)} (${d.count} items)`);
  
  svg.append('g')
    .call(d3.axisLeft(y))
    .selectAll('text')
    .style('font-size', '11px')
    .style('font-weight', '600')
    .style('fill', '#161823');
  
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(5))
    .selectAll('text')
    .style('font-size', '10px');
  
  svg.selectAll('.domain').remove();
  svg.selectAll('.tick line').attr('stroke', '#e8e8e8');
}

function createFoodFrequencyChart() {
  const foodArray = window.dashboardData.foodFrequency;
  if (!foodArray || foodArray.length === 0) return;
  
  const container = document.getElementById('food-frequency-chart');
  const margin = {top: 10, right: 40, bottom: 30, left: 120};
  const width = container.offsetWidth - margin.left - margin.right;
  const height = Math.max(300, foodArray.length * 40) - margin.top - margin.bottom;
  
  const svg = d3.select('#food-frequency-chart')
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);
  
  const y = d3.scaleBand()
    .range([0, height])
    .domain(foodArray.map(d => d.name))
    .padding(0.3);
  
  const x = d3.scaleLinear()
    .domain([0, d3.max(foodArray, d => d.count)])
    .range([0, width]);
  
  svg.selectAll('rect')
    .data(foodArray)
    .enter()
    .append('rect')
    .attr('y', d => y(d.name))
    .attr('x', 0)
    .attr('height', y.bandwidth())
    .attr('width', d => x(d.count))
    .attr('fill', '#00f2ea')
    .attr('rx', 3);
  
  svg.selectAll('.label')
    .data(foodArray)
    .enter()
    .append('text')
    .attr('y', d => y(d.name) + y.bandwidth() / 2)
    .attr('x', d => x(d.count) + 5)
    .attr('dy', '0.35em')
    .style('font-size', '11px')
    .style('font-weight', '700')
    .style('fill', '#161823')
    .text(d => `${d.count}x`);
  
  svg.append('g')
    .call(d3.axisLeft(y))
    .selectAll('text')
    .style('font-size', '11px')
    .style('font-weight', '600')
    .style('fill', '#161823');
  
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(5).tickFormat(d => Math.round(d)))
    .selectAll('text')
    .style('font-size', '10px');
  
  svg.selectAll('.domain').remove();
  svg.selectAll('.tick line').attr('stroke', '#e8e8e8');
}

function initializeTableFunctionality() {
  const searchInput = document.getElementById('search-input');
  const reviewsList = document.getElementById('reviews-list');
  const showMoreBtn = document.getElementById('show-more-btn');
  
  if (!reviewsList) return;
  
  const reviewRows = Array.from(reviewsList.querySelectorAll('.review-row'));
  const initialDisplayCount = 10;
  let showingAll = false;
  
  // Initially hide rows beyond the first 10
  reviewRows.forEach((row, index) => {
    if (index >= initialDisplayCount) {
      row.style.display = 'none';
    }
  });
  
  // Show more/fewer functionality
  if (showMoreBtn && reviewRows.length > initialDisplayCount) {
    showMoreBtn.addEventListener('click', () => {
      showingAll = !showingAll;
      
      reviewRows.forEach((row, index) => {
        if (index >= initialDisplayCount) {
          row.style.display = showingAll ? '' : 'none';
        }
      });
      
      const showMoreText = showMoreBtn.querySelector('.show-more-text');
      showMoreText.textContent = showingAll ? 'Show fewer' : 'Show more';
      showMoreBtn.classList.toggle('showing-all', showingAll);
    });
  } else if (showMoreBtn) {
    // Hide button if there are 10 or fewer reviews
    showMoreBtn.style.display = 'none';
  }
  
  // Accordion functionality
  reviewRows.forEach(row => {
    const header = row.querySelector('.review-row-header');
    header.addEventListener('click', () => {
      row.classList.toggle('expanded');
    });
  });
  
  // Search functionality
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      let visibleCount = 0;
      
      reviewRows.forEach((row, index) => {
        const rowText = row.textContent.toLowerCase();
        const matches = rowText.includes(query);
        
        // Handle visibility based on search and show more state
        if (matches) {
          if (showingAll || visibleCount < initialDisplayCount) {
            row.style.display = '';
            visibleCount++;
          } else {
            row.style.display = showingAll ? '' : 'none';
          }
        } else {
          row.style.display = 'none';
        }
      });
    });
  }
}
