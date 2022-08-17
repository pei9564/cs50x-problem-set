SELECT name
FROM people
JOIN stars
ON people.id = stars.person_id
WHERE person_id IN (
    SELECT person_id
    FROM stars
    JOIN movies
    ON movies.id = stars.movie_id
    WHERE title = 'Toy Story'
)
AND movie_id =(
    SELECT movie_id
    FROM stars
    JOIN movies
    ON movies.id = stars.movie_id
    WHERE title = 'Toy Story'
);