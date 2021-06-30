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
-- English
SELECT to_tsquery('cats | fishes');
SELECT to_tsquery('english', 'cats | fishes');
SELECT to_tsquery('english', 'The & Fat & Rats | stripes');

-- Danish
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
WHERE to_tsvector(description) @@ to_tsquery('english', 'cat & stripes');

-- Fast (hit index)
EXPLAIN ANALYZE
SELECT *
FROM search_animal
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'cat & stripes');

-- Fast (indexed tsvector)
EXPLAIN ANALYZE
SELECT *
FROM search_animal
WHERE description_tsv @@ to_tsquery('english', 'cat & stripes');
```

Ranking

```sql
-- The slowest (index missed)
SELECT ts_rank(to_tsvector(description), query) AS rank, *
FROM search_animal, to_tsquery('english', 'cat & stripes') AS query
WHERE to_tsvector(description) @@ query
ORDER BY rank DESC
LIMIT 10;

-- Slow (hit index)
SELECT ts_rank(to_tsvector('english', description), query) AS rank, *
FROM search_animal, to_tsquery('english', 'cat & stripes') AS query
WHERE to_tsvector('english', description) @@ query
ORDER BY rank DESC
LIMIT 10;

-- The Fastest (indexed tsvector)
SELECT ts_rank(description_tsv , query) AS rank, *
FROM search_animal, to_tsquery('cat & stripes') AS query
WHERE description_tsv @@ query
ORDER BY rank DESC
LIMIT 10;
```

# Experiment

```sql
--SELECT id from search_animal order by id desc limit 1;
--SELECT pg_size_pretty (pg_total_relation_size('search_animal'));
--DELETE FROM search_animal WHERE ID>10000;

-- Slow
SELECT *
FROM search_animal
WHERE description @@ to_tsquery('cat & stripes');

-- Slow
SELECT *
FROM search_animal
WHERE to_tsvector(description) @@ to_tsquery('cat & stripes');

-- Fast
SELECT *
FROM search_animal
WHERE to_tsvector('english', description) @@ to_tsquery('cat & stripes');

-- Fast
SELECT *
FROM search_animal
WHERE description_tsv @@ to_tsquery('cat & stripes');

-- Fast
SELECT ts_rank(description_tsv , to_tsquery('cat & stripes')) AS rank, *
FROM search_animal
WHERE description_tsv @@ to_tsquery('cat & stripes')
ORDER BY rank DESC

-- Slow
SELECT ts_rank(to_tsvector('english', description), to_tsquery('cat & stripes')) AS rank, *
FROM search_animal
WHERE to_tsvector('english', description) @@ to_tsquery('cat & stripes')
ORDER BY rank desc;
```

# Django ORM

```python
from search.models import Animal
from django.db import connection
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank

# Fast 0.2ms
Animal.objects.annotate(search=SearchVector('description')).filter(search='cats')
Animal.objects.annotate(search=SearchVector('description', config='english')).filter(search=SearchQuery('cats & stripes', config='english'))
Animal.objects.annotate(search=SearchVector('description_tsv', config='english')).filter(search=SearchQuery('cats & stripes', config='english', search_type='raw'))

# Slow
Animal.objects.annotate(rank=SearchRank('description', SearchQuery('cat & tiger | stripes'))).order_by('-rank')
Animal.objects.annotate(rank=SearchRank(SearchVector('description'), SearchQuery('cat & tiger | stripes'))).order_by('-rank')
Animal.objects.annotate(rank=SearchRank(SearchVector('description', config='english'), SearchQuery('cat & stripes', config='english'))).order_by('-rank')

Animal.objects.annotate(rank=SearchRank(CoalesceLessSearchVector('description', config='english'), SearchQuery('cat & stripes', config='english', search_type='raw'))).order_by('-rank')

# Fast
animals = Animal.objects.annotate(rank=SearchRank(VectorLessSearch('description_tsv'), SearchQuery('cat &
stripes', config='english', search_type='raw'))).order_by('-rank')

# Slow
Animal.objects.annotate(rank=SearchRank('description_tsv', SearchQuery('cat & stripes', config='english'))).order_by('-rank')
Animal.objects.annotate(rank=SearchRank(SearchVector('description_tsv'), SearchQuery('cat & stripes', config='english'))).order_by('-rank')
Animal.objects.annotate(rank=SearchRank(SearchVector('description_tsv', config='english'), SearchQuery('cat & stripes', config='english'))).order_by('-rank')

# Slow
Animal.objects.filter(description__search='stripes | cat')
# Fast
Animal.objects.filter(description__search=SearchQuery('stripes | cat', search_type='raw'))
Animal.objects.filter(description__search=SearchQuery('stripes | cat', search_type='raw',config='english'))

# Fast
Animal.objects.filter(description_tsv='cat | stripes')
Animal.objects.filter(description_tsv=SearchQuery('cat | stripes', search_type='raw'))

connection.queries[-1]['time']
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

# Benchmark

To run various benchmarks run

```bash
docker exec django-demo-app python manage.py benchmark
```

# Conclusions

Observations from experiment indicate that, gin indexed `to_tsvector(description)` column. is as fast as indexed `description_tsv` column updated with triggers. This is true only for `@@` operator. However, applying `to_tsvector('english', description)` in `ts_rank` function is not preferment as one would expect. Because of that I arrive to the conclusion that creating a `trigger` and `tsvcolumn` is not necessary if you need ONLY use `@@` operator that searches for queries. However, is still better to have `description_tsv` of `tsvcolumn` type because it works better with `ts_rank`.

To overcome limitations of auto generated queries created by Django ORM in Full Text Search I had to implement custom vectors.

#### API

```python
from django.db import connection

from search.models import Animal
from search.utils import CoalesceLessSearchVector
from search.utils import VectorLessSearch


>>> Animal.objects.annotate(rank=SearchRank(VectorLessSearch('description_tsv'), SearchQuery('cat & stripes', config='english', search_type='raw'))).order_by('-rank')
>>> connection.queries[-1]['time']
>>> connection.queries[-1]['sql']

>>> Animal.objects.annotate(search=CoalesceLessSearchVector('description', config='english')).filter(search=SearchQuery('cats', config='english', search_type='raw'))
>>> connection.queries[-1]['time']
>>> connection.queries[-1]['sql']

>>> Animal.objects.filter(description__search=SearchQuery('stripes | cat', config='english', search_type='raw'))
>>> connection.queries[-1]['time']
>>> connection.queries[-1]['sql']


```

#### /app/search/utils.py

```python
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.search import SearchVectorField


class VectorLessSearch(SearchVector):
    """
    Vector Less Search works ONLY with column that is tsvector datatype.
    link: https://github.com/django/django/blob/main/django/contrib/postgres/search.py
    """

    def as_sql(self, compiler, connection, function=None, template=None):
        clone = self.copy()
        config_sql = None
        config_params = []

        # Check if searched column is postgres tsvector datatype
        for expression in clone.get_source_expressions():
            if not isinstance(expression.output_field, SearchVectorField):
                raise Exception(f"Provided field '{expression.output_field}' is not a SearchVectorField (tsvector).")

        if template is None:
            if clone.config:
                config_sql, config_params = compiler.compile(clone.config)
                template = '%(function)s(%(config)s, %(expressions)s)'
            else:
                template = clone.template

        sql, params = super(SearchVector, clone).as_sql(
            compiler, connection, function=function, template=template,
            config=config_sql,
        )

        extra_params = []
        if clone.weight:
            weight_sql, extra_params = compiler.compile(clone.weight)
            sql = 'setweight({}, {})'.format(sql, weight_sql)

        # Remove postgres 'to_tsvector' function from sql string
        sql = sql.replace('to_tsvector(', '').replace(')', '')

        return sql, config_params + params + extra_params


class CoalesceLessSearchVector(SearchVector):
    """
    Class removes Coalesce and Cast functions from SearchVector.
    link: https://github.com/django/django/blob/main/django/contrib/postgres/search.py
    """

    def as_sql(self, compiler, connection, function=None, template=None):
        clone = self.copy()
        config_sql = None
        config_params = []
        if template is None:
            if clone.config:
                config_sql, config_params = compiler.compile(clone.config)
                template = '%(function)s(%(config)s, %(expressions)s)'
            else:
                template = clone.template

        sql, params = super(SearchVector, clone).as_sql(
            compiler, connection, function=function, template=template,
            config=config_sql,
        )

        extra_params = []
        if clone.weight:
            weight_sql, extra_params = compiler.compile(clone.weight)
            sql = 'setweight({}, {})'.format(sql, weight_sql)

        return sql, config_params + params + extra_params

```