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
