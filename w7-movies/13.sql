SELECT DISTINCT name
FROM people
JOIN stars
ON people.id = stars.person_id
WHERE movie_id IN (
    SELECT id
    FROM movies
    JOIN stars
    ON movies.id = stars.movie_id
    WHERE person_id = (
        SELECT id
        FROM people
        WHERE name = 'Kevin Bacon'
        AND birth = 1958
    )
)
AND name != 'Kevin Bacon';