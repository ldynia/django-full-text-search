# Description

This is a Django project set up for testing Full Text Searchi in PostgresQL.

# Instructions

```bash
$ docker-compose up
$ docker exec django-demo-app python manage.py migrate
$ docker exec django-demo-app python manage.py seed
```

# Links & Tutorials

* [Full Text Search](https://www.postgresql.org/docs/9.5/textsearch.html)
* [Postgres full-text search is Good Enough](http://rachbelaid.com/postgres-full-text-search-is-good-enough/)
* [Efficient Postgres Full Text Search in Django](https://pganalyze.com/blog/full-text-search-django-postgres)
* [How to use fuzzy string matching with Postgresql](https://www.freecodecamp.org/news/fuzzy-string-matching-with-postgresql/)

# Full text search

Restart index.

```sql
TRUNCATE TABLE search_artist;
ALTER SEQUENCE search_artist_id_seq RESTART WITH 1;
```

Create tsvector and index columns.

```sql
ALTER TABLE search_animal ADD COLUMN description_tsv tsvector;
UPDATE search_animal SET description_tsv = to_tsvector('english', description);
CREATE INDEX description_idx_gin ON search_animal USING GIN(to_tsvector('english', description));
CREATE INDEX description_tsv_idx_gin ON search_animal USING GIN(description_tsv);
```


Queries & Vectors & Ranking

```sql
-- Query
SELECT to_tsquery('cats | fishes');
SELECT to_tsquery('english', 'cats | fishes');
SELECT to_tsquery('english', 'The & Fat & Rats | stripes');

SELECT to_tsquery('katten | fisken');
SELECT to_tsquery('danish', 'katten | fisken');

-- Vector
SELECT to_tsvector('english', 'Cats is plular from a cat. The cats is a musical')

-- Rankings
SELECT ts_rank(to_tsvector('english', 'in the list of stop words'), to_tsquery('list & stop'));
SELECT ts_rank_cd(to_tsvector('english', 'list stop words'), to_tsquery('list & stop'));
```

Full Text Search

```sql
-- Slow (missed index)
EXPLAIN ANALYZE
SELECT *
FROM search_animal
WHERE description @@ 'cat & stripes';

-- Slow (missed index)
EXPLAIN ANALYZE
SELECT *
FROM search_animal
WHERE to_tsvector(description) @@ to_tsquery('cat & stripes');

-- Fast (hit index)
EXPLAIN ANALYZE
SELECT *
FROM search_animal
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'cat & stripes');

-- Fast (indexed tsvector)
EXPLAIN ANALYZE
SELECT *
FROM search_animal
WHERE description_tsv @@ to_tsquery('cat & stripes');

-- Fast (indexed tsvector)
EXPLAIN ANALYZE
SELECT *
FROM search_animal
WHERE description_tsv @@ to_tsquery('english', 'cat & stripes');
```

Ranking

```sql
-- Slow (index missed)
SELECT ts_rank_cd(to_tsvector(description), query) AS rank, *
FROM search_animal, to_tsquery('tiger|(stripes & cat)') AS query
WHERE to_tsvector(description) @@ query
ORDER BY rank DESC
LIMIT 10;

-- Faster (hit index)
SELECT ts_rank_cd(to_tsvector('english', description), query) AS rank, *
FROM search_animal, to_tsquery('english', 'tiger|(stripes & cat)') query
WHERE to_tsvector('english', description) @@ query
ORDER BY rank DESC
LIMIT 10;

-- Faster (hit index)
SELECT ts_rank(to_tsvector('english', description) , to_tsquery('cat & stripes')) AS rank, *
FROM search_animal
WHERE to_tsvector('english', description) @@ to_tsquery('cat & stripes')
ORDER BY rank DESC
LIMIT 10;

-- The Fastest (indexed tsvector)
SELECT ts_rank(description_tsv , query) AS rank, *
FROM search_animal, to_tsquery('cat & stripes') AS query
WHERE description_tsv @@ to_tsquery('cat & stripes')
ORDER BY rank DESC
LIMIT 10;

-- The Fastest (indexed tsvector)
SELECT ts_rank_cd(description_tsv , to_tsquery('cat & stripes')) AS rank, *
FROM search_animal
WHERE description_tsv @@ to_tsquery('cat & stripes')
ORDER BY rank DESC
LIMIT 10;
```

# Django ORM

```python
from search.models import Animal
from django.db.models import F
from django.db import connection
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank

Animal.objects.annotate(search=SearchVector('description')).filter(search='cats')
Animal.objects.annotate(search=SearchVector('description', config='english')).filter(search=SearchQuery('cats & stripes', config='english'))
Animal.objects.annotate(search=SearchVector('description_tsv', config='english')).filter(search=SearchQuery('cats & stripes', config='english'))

# Slow
Animal.objects.annotate(rank=SearchRank('description', SearchQuery('cat & tiger | stripes'))).order_by('-rank')
Animal.objects.annotate(rank=SearchRank(SearchVector('description'), SearchQuery('cat & tiger | stripes'))).order_by('-rank')
Animal.objects.annotate(rank=SearchRank(SearchVector('description', config='english'), SearchQuery('cat & stripes', config='english'))).order_by('-rank')

# Slow
Animal.objects.annotate(rank=SearchRank('description_tsv', SearchQuery('cat & stripes', config='english'))).order_by('-rank')
Animal.objects.annotate(rank=SearchRank(SearchVector('description_tsv'), SearchQuery('cat & stripes'))).order_by('-rank')
Animal.objects.annotate(rank=SearchRank(SearchVector('description_tsv', config='english'), SearchQuery('cat & stripes', config='english'))).order_by('-rank')

# Slow
Animal.objects.filter(description__search='stripes & cat')
Animal.objects.filter(description__search=SearchQuery('stripes & cat'))
Animal.objects.filter(description__search=SearchQuery('stripes & cat', config='english'))

# Fast
Animal.objects.filter(description_tsv='cat | stripes')
Animal.objects.filter(description_tsv=SearchQuery('cat | stripes'))
Animal.objects.filter(description_tsv=SearchQuery('cat | stripes', config='english'))
```

# Fuzzy Search

```sql
-- Wildcard filters
SELECT *
FROM search_artist
WHERE name LIKE 'Barbara%'
AND name LIKE '%Hep%';

-- CREATE EXTENSION pg_trgm;
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