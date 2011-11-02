CREATE TABLE dmoz_sphinxse
(
    id          INTEGER UNSIGNED NOT NULL,
    weight      INTEGER NOT NULL,
    query       VARCHAR(3072) NOT NULL,
    title       VARCHAR(3072),
    description VARCHAR(3072),
    url         VARCHAR(255),
    topic       VARCHAR(3072),
    INDEX(query)
) ENGINE=SPHINX CONNECTION="sphinx://127.0.0.1:9312/directory_search_index";
