document.addEventListener('DOMContentLoaded', function() {
    const userSelect = document.getElementById('userSelect');
    const getRecommendationsBtn = document.getElementById('getRecommendations');
    const loadingSection = document.getElementById('loadingSection');
    const userRatingsSection = document.getElementById('userRatingsSection');
    const recommendationsSection = document.getElementById('recommendationsSection');
    const userRatingsContainer = document.getElementById('userRatings');
    const recommendationsContainer = document.getElementById('recommendations');

    // Debounce function to prevent multiple rapid requests
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Enable/disable button based on user selection
    userSelect.addEventListener('change', function() {
        getRecommendationsBtn.disabled = !this.value;
        // Clear previous results when user changes
        if (!this.value) {
            hideAllSections();
        }
    });

    // Handle get recommendations button click with debouncing
    const debouncedGetRecommendations = debounce(function() {
        const userId = userSelect.value;
        if (!userId) return;

        // Show loading with better UX
        showLoading();
        
        // Get user ratings and recommendations in parallel
        Promise.all([
            getUserRatings(userId),
            getRecommendations(userId)
        ]).then(() => {
            hideLoading();
        }).catch(error => {
            console.error('Error:', error);
            hideLoading();
            showError('Something went wrong. Please try again.');
        });
    }, 300);

    getRecommendationsBtn.addEventListener('click', debouncedGetRecommendations);

    function showLoading() {
        loadingSection.style.display = 'block';
        userRatingsSection.style.display = 'none';
        recommendationsSection.style.display = 'none';
        
        // Disable button during loading
        getRecommendationsBtn.disabled = true;
        getRecommendationsBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    }

    function hideLoading() {
        loadingSection.style.display = 'none';
        
        // Re-enable button
        getRecommendationsBtn.disabled = false;
        getRecommendationsBtn.innerHTML = '<i class="fas fa-magic"></i> Get Recommendations';
    }

    function hideAllSections() {
        loadingSection.style.display = 'none';
        userRatingsSection.style.display = 'none';
        recommendationsSection.style.display = 'none';
    }

    function showError(message) {
        recommendationsContainer.innerHTML = `
            <div style="text-align: center; color: #e74c3c; padding: 20px;">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 10px;"></i>
                <p>${message}</p>
            </div>
        `;
        recommendationsSection.style.display = 'block';
    }

    async function getUserRatings(userId) {
        try {
            const formData = new FormData();
            formData.append('user_id', userId);

            const response = await fetch('/get_user_ratings', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to fetch user ratings');
            }

            const data = await response.json();
            displayUserRatings(data);
        } catch (error) {
            console.error('Error fetching user ratings:', error);
            throw error;
        }
    }

    async function getRecommendations(userId) {
        try {
            const formData = new FormData();
            formData.append('user_id', userId);

            const response = await fetch('/get_recommendations', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to fetch recommendations');
            }

            const data = await response.json();
            displayRecommendations(data);
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            throw error;
        }
    }

    function displayUserRatings(ratings) {
        if (ratings.length === 0) {
            userRatingsContainer.innerHTML = `
                <div style="text-align: center; color: #666; padding: 20px;">
                    <i class="fas fa-info-circle" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <p>No ratings found for this user.</p>
                </div>
            `;
        } else {
            // Show only first 10 ratings for better performance
            const displayRatings = ratings.slice(0, 10);
            userRatingsContainer.innerHTML = displayRatings.map(rating => `
                <div class="movie-card" style="animation-delay: ${Math.random() * 0.5}s;">
                    <h3>${rating.title}</h3>
                    <div class="genre">${rating.genre}</div>
                    <div class="rating">
                        <span class="stars">${'★'.repeat(rating.rating)}${'☆'.repeat(5-rating.rating)}</span>
                        <span>(${rating.rating}/5)</span>
                    </div>
                </div>
            `).join('');
            
            if (ratings.length > 10) {
                userRatingsContainer.innerHTML += `
                    <div style="text-align: center; color: #666; padding: 10px; grid-column: 1 / -1;">
                        <p>Showing first 10 of ${ratings.length} ratings</p>
                    </div>
                `;
            }
        }
        userRatingsSection.style.display = 'block';
    }

    function displayRecommendations(recommendations) {
        if (recommendations.length === 0) {
            recommendationsContainer.innerHTML = `
                <div style="text-align: center; color: #666; padding: 20px;">
                    <i class="fas fa-lightbulb" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <p>No recommendations available for this user.</p>
                </div>
            `;
        } else {
            recommendationsContainer.innerHTML = recommendations.map((rec, index) => `
                <div class="movie-card" style="animation-delay: ${index * 0.1}s;">
                    <h3>${rec.title}</h3>
                    <div class="genre">${rec.genre}</div>
                    <div class="score">Recommendation Score: ${rec.score}</div>
                </div>
            `).join('');
        }
        recommendationsSection.style.display = 'block';
    }

    // Add smooth scrolling for better UX
    function scrollToElement(element) {
        element.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    // Scroll to recommendations when they load
    const originalDisplayRecommendations = displayRecommendations;
    displayRecommendations = function(recommendations) {
        originalDisplayRecommendations(recommendations);
        setTimeout(() => {
            scrollToElement(recommendationsSection);
        }, 100);
    };

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && userSelect === document.activeElement) {
            e.preventDefault();
            if (!getRecommendationsBtn.disabled) {
                debouncedGetRecommendations();
            }
        }
    });

    // Add some interactive effects with performance optimization
    let animationFrame;
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('movie-card')) {
            if (animationFrame) {
                cancelAnimationFrame(animationFrame);
            }
            
            animationFrame = requestAnimationFrame(() => {
                e.target.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    e.target.style.transform = '';
                }, 150);
            });
        }
    });

    // Preload data for better perceived performance
    function preloadData() {
        // Preload the first user's data in the background
        if (userSelect.options.length > 1) {
            const firstUserId = userSelect.options[1].value;
            setTimeout(() => {
                getUserRatings(firstUserId).catch(() => {
                    // Silently fail for preloading
                });
            }, 2000);
        }
    }

    // Initialize preloading after a delay
    setTimeout(preloadData, 1000);
}); 