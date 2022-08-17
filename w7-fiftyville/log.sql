-- Keep a log of any SQL queries you execute as you solve the mystery.

-- ## Initial INF:
-- took place on July 28, 2021 and that it took place on Humphrey Street.

SELECT * FROM crime_scene_reports WHERE month = 7 AND day = 28 AND street = 'Humphrey Street';
-- ## FIND creime report:
-- Theft of the CS50 duck took place at 10:15am at the Humphrey Street bakery.
-- Interviews were conducted today with three witnesses who were present at the time – each of their interview transcripts mentions the bakery.

SELECT * FROM interviews WHERE year = 2021 AND month = 7 AND day = 28 AND transcript LIKE '%bakery%';
-- ## FIND interview which mention bakery.
-- 01. Ruth: Sometime within ten minutes of the theft, I saw the thief get into a car in the bakery parking lot and drive away.
-- 02. Eugene: before I arrived at Emma's bakery, I was walking by the ATM on Leggett Street and saw the thief there withdrawing some money.
-- 03. Raymond: thief called someone who talked to them for less than a minute.
--              they were planning to take the earliest flight out of Fiftyville tomorrow.
--              The thief then asked the person on the other end of the phone to purchase the flight ticket.

-- ## LOOK for the clue in three interviews
SELECT * FROM bakery_security_logs WHERE year = 2021 AND month = 7 AND day = 28 AND hour = 10 AND minute < 30;
SELECT * FROM atm_transactions WHERE year = 2021 AND month = 7 AND day = 28 AND atm_location = 'Leggett Street' AND transaction_type = 'withdraw';
SELECT * FROM phone_calls WHERE year = 2021 AND month = 7 AND day = 28 AND duration < 60;

-- ## FIND someone who matched the clues
SELECT * FROM people JOIN bank_accounts ON people.id = bank_accounts.person_id

WHERE account_number IN (
    SELECT account_number
    FROM atm_transactions
        WHERE year = 2021
        AND month = 7
        AND day = 28
        AND atm_location = 'Leggett Street'
        AND transaction_type = 'withdraw')

AND phone_number IN (
    SELECT caller
    FROM phone_calls
        WHERE year = 2021
        AND month = 7
        AND day = 28
        AND duration < 60)

AND license_plate IN (
    SELECT license_plate
        FROM bakery_security_logs
        WHERE year = 2021
        AND month = 7
        AND day = 28
        AND hour = 10
        AND minute < 30);

-- ## LEFT two suspects
-- +--------+-------+----------------+-----------------+---------------+----------------+-----------+---------------+
-- |   id   | name  |  phone_number  | passport_number | license_plate | account_number | person_id | creation_year |
-- +--------+-------+----------------+-----------------+---------------+----------------+-----------+---------------+
-- | 686048 | Bruce | (367) 555-5533 | 5773159633      | 94KL13X       | 49610011       | 686048    | 2010          |
-- | 514354 | Diana | (770) 555-1861 | 3592750733      | 322W7JE       | 26013199       | 514354    | 2012          |
-- +--------+-------+----------------+-----------------+---------------+----------------+-----------+---------------+

-- ## LOOK for the earliest flight on July 29
SELECT *
FROM flights
JOIN airports
ON flights.origin_airport_id = airports.id
WHERE day = 29
AND city = 'Fiftyville'
ORDER BY hour LIMIT 1;

-- +----+-------------------+------------------------+------+-------+-----+------+--------+----+--------------+-----------------------------+------------+
-- | id | origin_airport_id | destination_airport_id | year | month | day | hour | minute | id | abbreviation |          full_name          |    city    |
-- +----+-------------------+------------------------+------+-------+-----+------+--------+----+--------------+-----------------------------+------------+
-- | 36 | 8                 | 4                      | 2021 | 7     | 29  | 8    | 20     | 8  | CSF          | Fiftyville Regional Airport | Fiftyville |
-- +----+-------------------+------------------------+------+-------+-----+------+--------+----+--------------+-----------------------------+------------+

-- ## LOOK for two suspects' flight record
SELECT *
FROM passengers
JOIN flights
ON passengers.flight_id = flights.id
WHERE
    passport_number = 3592750733
    OR passport_number = 5773159633;
-- +-----------+-----------------+------+----+-------------------+------------------------+------+-------+-----+------+--------+
-- | flight_id | passport_number | seat | id | origin_airport_id | destination_airport_id | year | month | day | hour | minute |
-- +-----------+-----------------+------+----+-------------------+------------------------+------+-------+-----+------+--------+
-- | 18        | 3592750733      | 4C   | 18 | 8                 | 6                      | 2021 | 7     | 29  | 16   | 0      |
-- | 24        | 3592750733      | 2C   | 24 | 7                 | 8                      | 2021 | 7     | 30  | 16   | 27     |
-- | 36        | 5773159633      | 4A   | 36 | 8                 | 4                      | 2021 | 7     | 29  | 8    | 20     |
-- | 54        | 3592750733      | 6C   | 54 | 8                 | 5                      | 2021 | 7     | 30  | 10   | 19     |
-- +-----------+-----------------+------+----+-------------------+------------------------+------+-------+-----+------+--------+


-- # GET the THIEF is Bruce
-- # He HIDE in New York City

-- ## FIND the person who talked to Bruce in bakery
SELECT *
FROM people
WHERE phone_number = (
    SELECT receiver FROM phone_calls
    WHERE year = 2021
    AND month = 7
    AND day = 28
    AND duration < 60
    AND caller = (
        SELECT phone_number
        FROM people
        WHERE name = 'Bruce'));

-- # GET the HELPER is Robin