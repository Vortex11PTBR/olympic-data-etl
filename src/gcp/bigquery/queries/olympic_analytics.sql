-- Olympic Analytics: BigQuery SQL Queries
-- Production-grade queries with partitioning, clustering, and query optimization

-- ============================================================================
-- 1. MEDAL COUNTS BY COUNTRY (WITH YEAR-OVER-YEAR COMPARISON)
-- ============================================================================

-- Query 1.1: Current medal count by country (all-time)
-- Partitioned by year, clustered by country for optimal performance
SELECT
    country_code,
    country_name,
    region,
    COUNTIF(medal_type = 'GOLD') as gold_medals,
    COUNTIF(medal_type = 'SILVER') as silver_medals,
    COUNTIF(medal_type = 'BRONZE') as bronze_medals,
    COUNT(*) as total_medals,
    RANK() OVER (ORDER BY COUNT(*) DESC) as overall_rank,
    MIN(year) as first_medal_year,
    MAX(year) as last_medal_year
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
WHERE
    year <= 2024
GROUP BY
    country_code, country_name, region
ORDER BY
    total_medals DESC;

-- Query 1.2: Year-over-year medal comparison
SELECT
    country_code,
    country_name,
    year,
    COUNTIF(medal_type = 'GOLD') as gold_medals,
    COUNTIF(medal_type = 'SILVER') as silver_medals,
    COUNTIF(medal_type = 'BRONZE') as bronze_medals,
    COUNT(*) as total_medals,
    LAG(COUNT(*)) OVER (
        PARTITION BY country_code 
        ORDER BY year
    ) as previous_year_total,
    ROUND(
        (COUNT(*) - LAG(COUNT(*)) OVER (
            PARTITION BY country_code 
            ORDER BY year
        )) / LAG(COUNT(*)) OVER (
            PARTITION BY country_code 
            ORDER BY year
        ) * 100, 
        2
    ) as yoy_growth_percent
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
WHERE
    year BETWEEN 2000 AND 2024
GROUP BY
    country_code, country_name, year
ORDER BY
    year DESC, total_medals DESC;

-- Query 1.3: Top 10 countries by medal count in specific Olympic Games
SELECT
    country_code,
    country_name,
    year,
    season,
    city,
    COUNTIF(medal_type = 'GOLD') as gold_medals,
    COUNTIF(medal_type = 'SILVER') as silver_medals,
    COUNTIF(medal_type = 'BRONZE') as bronze_medals,
    COUNT(*) as total_medals,
    RANK() OVER (
        PARTITION BY year 
        ORDER BY COUNT(*) DESC
    ) as rank_in_games
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
WHERE
    year = 2020  -- Change year as needed
GROUP BY
    country_code, country_name, year, season, city
ORDER BY
    total_medals DESC
LIMIT 10;


-- ============================================================================
-- 2. ATHLETE PERFORMANCE ANALYTICS
-- ============================================================================

-- Query 2.1: Top athletes by medal count
SELECT
    athlete_id,
    athlete_name,
    country_code,
    country_name,
    COUNTIF(medal_type = 'GOLD') as gold_medals,
    COUNTIF(medal_type = 'SILVER') as silver_medals,
    COUNTIF(medal_type = 'BRONZE') as bronze_medals,
    COUNT(*) as total_medals,
    COUNT(DISTINCT year) as olympics_participated,
    COUNT(DISTINCT event_id) as sports_events,
    RANK() OVER (ORDER BY COUNT(*) DESC) as overall_rank
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
GROUP BY
    athlete_id, athlete_name, country_code, country_name
HAVING
    COUNT(*) >= 3  -- Athletes with at least 3 medals
ORDER BY
    total_medals DESC
LIMIT 100;

-- Query 2.2: Multi-Olympics athletes (career progression)
SELECT
    athlete_id,
    athlete_name,
    country_code,
    country_name,
    ARRAY_AGG(
        STRUCT(
            year,
            season,
            city,
            medal_type,
            event_id
        )
        ORDER BY year
    ) as medal_history,
    COUNT(DISTINCT year) as olympics_count,
    MIN(year) as debut_year,
    MAX(year) as last_year,
    MAX(year) - MIN(year) as years_span,
    COUNT(*) as total_medals
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
GROUP BY
    athlete_id, athlete_name, country_code, country_name
HAVING
    COUNT(DISTINCT year) >= 2
ORDER BY
    olympics_count DESC, total_medals DESC;

-- Query 2.3: Athlete performance by sport
SELECT
    event_id,
    event_name,
    sport,
    COUNT(*) as total_medals_awarded,
    COUNT(DISTINCT athlete_id) as unique_athletes,
    COUNTIF(medal_type = 'GOLD') as gold_medals,
    COUNTIF(medal_type = 'SILVER') as silver_medals,
    COUNTIF(medal_type = 'BRONZE') as bronze_medals,
    COUNT(DISTINCT country_code) as countries_represented,
    COUNT(DISTINCT year) as olympics_held
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
GROUP BY
    event_id, event_name, sport
ORDER BY
    total_medals_awarded DESC;


-- ============================================================================
-- 3. HISTORICAL TRENDS (1896-2024)
-- ============================================================================

-- Query 3.1: Medal trends over decades
SELECT
    CASE
        WHEN year < 1920 THEN '1896-1920'
        WHEN year < 1950 THEN '1920-1950'
        WHEN year < 1980 THEN '1950-1980'
        WHEN year < 2010 THEN '1980-2010'
        ELSE '2010-2024'
    END as decade,
    COUNT(DISTINCT year) as olympics_held,
    COUNT(*) as total_medals,
    COUNT(DISTINCT country_code) as countries_participated,
    COUNT(DISTINCT athlete_id) as athletes_medaled,
    COUNT(DISTINCT event_id) as total_events,
    ROUND(AVG(COUNTIF(medal_type = 'GOLD')), 2) as avg_gold_per_olympics,
    ROUND(AVG(COUNT(*)), 2) as avg_medals_per_olympics
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
GROUP BY
    decade
ORDER BY
    decade;

-- Query 3.2: Summer vs Winter Olympics comparison
SELECT
    season,
    year,
    city,
    COUNT(*) as total_medals,
    COUNT(DISTINCT athlete_id) as athletes,
    COUNT(DISTINCT country_code) as countries,
    COUNT(DISTINCT event_id) as events,
    COUNTIF(medal_type = 'GOLD') as gold_medals,
    COUNTIF(medal_type = 'SILVER') as silver_medals,
    COUNTIF(medal_type = 'BRONZE') as bronze_medals
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
WHERE
    season IN ('Summer', 'Winter')
GROUP BY
    season, year, city
ORDER BY
    year DESC;

-- Query 3.3: Growth trend analysis (total medals by year)
SELECT
    year,
    season,
    city,
    COUNT(*) as medal_count,
    COUNT(DISTINCT country_code) as countries,
    LAG(COUNT(*)) OVER (ORDER BY year) as previous_olympics_medals,
    ROUND(
        (COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY year)) / 
        LAG(COUNT(*)) OVER (ORDER BY year) * 100, 
        2
    ) as growth_percent
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
WHERE
    year >= 1896
GROUP BY
    year, season, city
ORDER BY
    year DESC;


-- ============================================================================
-- 4. GEOGRAPHIC DISTRIBUTION
-- ============================================================================

-- Query 4.1: Medals by geographic region
SELECT
    region,
    COUNT(*) as total_medals,
    COUNT(DISTINCT country_code) as countries,
    COUNT(DISTINCT athlete_id) as athletes,
    COUNTIF(medal_type = 'GOLD') as gold_medals,
    COUNTIF(medal_type = 'SILVER') as silver_medals,
    COUNTIF(medal_type = 'BRONZE') as bronze_medals,
    ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 2) as percent_of_total_medals,
    RANK() OVER (ORDER BY COUNT(*) DESC) as region_rank
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
WHERE
    region IS NOT NULL
GROUP BY
    region
ORDER BY
    total_medals DESC;

-- Query 4.2: Geographic dominance by year
SELECT
    year,
    region,
    COUNT(*) as medals,
    RANK() OVER (
        PARTITION BY year 
        ORDER BY COUNT(*) DESC
    ) as rank_in_year
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
WHERE
    region IS NOT NULL
GROUP BY
    year, region
ORDER BY
    year DESC, rank_in_year;

-- Query 4.3: Emerging nations (first medals and growth)
SELECT
    country_code,
    country_name,
    region,
    MIN(year) as first_medal_year,
    MAX(year) as most_recent_medal_year,
    COUNT(DISTINCT year) as olympics_with_medals,
    COUNT(*) as total_medals,
    COUNTIF(medal_type = 'GOLD') as gold_medals,
    CASE
        WHEN MAX(year) >= 2020 THEN 'Active'
        WHEN MAX(year) >= 2010 THEN 'Semi-Active'
        ELSE 'Historical'
    END as status
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
GROUP BY
    country_code, country_name, region
HAVING
    MIN(year) >= 1980  -- Nations with first medals after 1980
ORDER BY
    first_medal_year DESC, total_medals DESC;


-- ============================================================================
-- 5. ADVANCED ANALYTICS & INSIGHTS
-- ============================================================================

-- Query 5.1: Medal concentration analysis (Herfindahl index)
SELECT
    year,
    -- Calculate medal concentration (higher = more concentrated)
    ROUND(
        SUM(POW(CAST(medal_count AS FLOAT64) / total_medals_year, 2)), 
        4
    ) as concentration_index,
    total_medals_year,
    num_countries,
    CASE
        WHEN SUM(POW(CAST(medal_count AS FLOAT64) / total_medals_year, 2)) > 0.25 THEN 'Highly Concentrated'
        WHEN SUM(POW(CAST(medal_count AS FLOAT64) / total_medals_year, 2)) > 0.15 THEN 'Moderately Concentrated'
        ELSE 'Distributed'
    END as concentration_level
FROM (
    SELECT
        year,
        country_code,
        COUNT(*) as medal_count,
        SUM(COUNT(*)) OVER (PARTITION BY year) as total_medals_year,
        COUNT(DISTINCT country_code) OVER (PARTITION BY year) as num_countries
    FROM
        `{PROJECT_ID}.olympic_analytics.medals`
    GROUP BY
        year, country_code
)
GROUP BY
    year, total_medals_year, num_countries
ORDER BY
    year DESC;

-- Query 5.2: Host nation advantage analysis
SELECT
    year,
    city,
    season,
    host_country,
    COUNT(*) as host_medals,
    SUM(COUNT(*)) OVER (PARTITION BY year) as total_medals,
    ROUND(COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY year) * 100, 2) as host_medal_percent,
    RANK() OVER (
        PARTITION BY year 
        ORDER BY COUNT(*) DESC
    ) as host_rank
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
WHERE
    country_code = SUBSTR(city, -3)  -- Simplified host country matching
GROUP BY
    year, city, season, host_country
ORDER BY
    year DESC;

-- Query 5.3: Sports dominance by country
SELECT
    country_code,
    country_name,
    ARRAY_AGG(
        STRUCT(
            sport,
            medal_count
        )
        ORDER BY medal_count DESC
        LIMIT 5
    ) as top_sports
FROM (
    SELECT
        country_code,
        country_name,
        event_name as sport,
        COUNT(*) as medal_count
    FROM
        `{PROJECT_ID}.olympic_analytics.medals`
    GROUP BY
        country_code, country_name, sport
)
GROUP BY
    country_code, country_name
HAVING
    SUM(medal_count) >= 10
ORDER BY
    SUM(medal_count) DESC;


-- ============================================================================
-- 6. DATA QUALITY & MONITORING
-- ============================================================================

-- Query 6.1: Data completeness check
SELECT
    COUNTIF(athlete_id IS NOT NULL) as records_with_athlete_id,
    COUNTIF(country_code IS NOT NULL) as records_with_country,
    COUNTIF(medal_type IS NOT NULL) as records_with_medal_type,
    COUNTIF(year IS NOT NULL) as records_with_year,
    COUNT(*) as total_records,
    ROUND(COUNTIF(athlete_id IS NOT NULL) / COUNT(*) * 100, 2) as athlete_completeness_pct,
    ROUND(COUNTIF(country_code IS NOT NULL) / COUNT(*) * 100, 2) as country_completeness_pct
FROM
    `{PROJECT_ID}.olympic_analytics.medals`;

-- Query 6.2: Duplicate detection
SELECT
    athlete_id,
    event_id,
    year,
    medal_type,
    country_code,
    COUNT(*) as duplicate_count
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
GROUP BY
    athlete_id, event_id, year, medal_type, country_code
HAVING
    COUNT(*) > 1
ORDER BY
    duplicate_count DESC;

-- Query 6.3: Recent data freshness
SELECT
    'medals' as table_name,
    MAX(processed_at) as last_updated,
    TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(processed_at), HOUR) as hours_since_update,
    COUNT(*) as current_row_count,
    COUNT(DISTINCT DATE(processed_at)) as days_with_updates
FROM
    `{PROJECT_ID}.olympic_analytics.medals`
WHERE
    processed_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY);


-- ============================================================================
-- 7. PRACTICAL DASHBOARD QUERIES
-- ============================================================================

-- Query 7.1: Summary stats for dashboard (single query)
WITH country_stats AS (
    SELECT
        COUNT(DISTINCT country_code) as total_countries,
        COUNT(DISTINCT athlete_id) as total_athletes,
        COUNT(DISTINCT event_id) as total_events,
        COUNT(*) as total_medals,
        COUNTIF(medal_type = 'GOLD') as total_golds
    FROM
        `{PROJECT_ID}.olympic_analytics.medals`
    WHERE
        year <= 2024
)
SELECT
    cs.total_countries,
    cs.total_athletes,
    cs.total_events,
    cs.total_medals,
    cs.total_golds,
    ROUND(cs.total_golds / cs.total_medals * 100, 2) as gold_medal_percentage
FROM
    country_stats cs;

-- Query 7.2: Top 10 countries + their latest Olympics appearance
SELECT
    m.country_code,
    m.country_name,
    SUM(CASE WHEN m.medal_type = 'GOLD' THEN 1 ELSE 0 END) as gold_count,
    SUM(CASE WHEN m.medal_type = 'SILVER' THEN 1 ELSE 0 END) as silver_count,
    SUM(CASE WHEN m.medal_type = 'BRONZE' THEN 1 ELSE 0 END) as bronze_count,
    COUNT(*) as total_medals,
    MAX(m.year) as latest_olympics_year,
    RANK() OVER (ORDER BY COUNT(*) DESC) as rank
FROM
    `{PROJECT_ID}.olympic_analytics.medals` m
GROUP BY
    m.country_code, m.country_name
ORDER BY
    rank
LIMIT 10;
