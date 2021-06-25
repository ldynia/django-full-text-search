# Description

Plain django init project.

# Instructions

```bash
$ docker-compose up
$ docker exec django-demo-app python manage.py seed
```

# Links

* [Full Text Search](https://www.postgresql.org/docs/9.5/textsearch.html)
* [Fuzzy Search I](https://www.freecodecamp.org/news/fuzzy-string-matching-with-postgresql/)
* [Fuzzy Search II](http://rachbelaid.com/postgres-full-text-search-is-good-enough/)

# SQL

### Full text search

```sql
--TRUNCATE TABLE search_artist;
-- ALTER SEQUENCE search_artist_id_seq RESTART WITH 1;

-- Concatenate columns
SELECT description FROM search_animal;
SELECT name || ' ' || description as document
FROM search_animal;

-- Full text search
SELECT description
FROM search_animal
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'cat & fish');

-- Create index
CREATE INDEX description_idx ON search_animal USING GIN(to_tsvector('english', description));

-- Vector
SELECT to_tsvector('english', 'in the list of stop words');
SELECT to_tsvector('english', 'a fat  cat sat on a mat - it ate a fat rats');
SELECT ts_rank_cd(to_tsvector('english', 'in the list of stop words'), to_tsquery('list & stop'));
SELECT ts_rank_cd(to_tsvector('english', 'list stop words'), to_tsquery('list & stop'));

-- Query
SELECT to_tsquery('english', 'The & Fat & Rats');

-- Ranking
SELECT name, ts_rank_cd(to_tsvector('english', description), query) AS rank
FROM search_animal, to_tsquery('english', 'tiger|(stripes & cat)') query
WHERE query @@ to_tsvector(description)
ORDER BY rank desc
LIMIT 10;
```


### Fuzzy Search

```sql
-- Wildcard filters
SELECT *
FROM search_artist
WHERE name LIKE 'Barbara%'
AND name LIKE '%Hep%';


--CREATE EXTENSION pg_trgm;
-- Wildcard trigrams
SELECT *
FROM search_artist
WHERE SIMILARITY(name,'Claud Monday') > 0.3 ;

SELECT *
FROM search_artist
WHERE name % 'Claud Monday';

SELECT *
FROM search_artist
ORDER BY SIMILARITY(name,'Lee Casner') DESC
LIMIT 5;

SELECT *
FROM search_artist sa
WHERE 'Cadinsky' % ANY(STRING_TO_ARRAY(name,' '));

-- CREATE EXTENSION fuzzystrmatch;
SELECT *
FROM search_artist
WHERE nationality IN ('American', 'British', '')
AND SOUNDEX(name) = SOUNDEX('Damian Hurst');

SELECT *, LEVENSHTEIN(name, 'Freda Kallo')
FROM search_artist
ORDER BY LEVENSHTEIN(name, 'Freda Kallo') ASC
LIMIT 5;


SELECT similarity('Something', 'something');

select name, description @@ to_tsquery('tiger | fish') as res
from search_animal
order by res desc;

```
# Django ORM

```python
from search.models import Animal
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

Animal.objects.annotate(rank=SearchRank(SearchVector('description'), SearchQuery('stripes'))).order_by('-rank')
Animal.objects.annotate(rank=SearchRank(SearchVector('description'), SearchQuery('tiger stripes'))).order_by('-rank')
Animal.objects.annotate(rank=SearchRank(SearchVector('description'), SearchQuery('stripes & tiger | fish'))).order_by('-rank')
Animal.objects.filter(description__search='tiger | fish')
Animal.objects.filter(description__search=SearchQuery('tiger | fish'))


```