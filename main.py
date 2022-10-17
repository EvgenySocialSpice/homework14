import json
import sqlite3
import flask

app = flask.Flask(__name__)


def get_value_from_db(sql):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        result = connection.execute(sql).fetchall()
        return result


def search_by_title(title):
    sql = f'''
            SELECT title, country, release_year, listed_in, description
            FROM netflix
            WHERE title = '{title}'
            ORDER BY release_year DESC
            LIMIT 1
        '''
    result = get_value_from_db(sql)
    for item in result:
        return dict(item)


@app.get("/movie/<title>/")
def search_by_title_view(title):
    result = search_by_title(title=title)
    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=4),
        status=200,
        mimetype="application/json"
    )


@app.get("/movie/<int:year1>/to/<int:year2>/")
def search_by_release_year_view(year1, year2):
    year1 = int(year1)
    year2 = int(year2)
    sql = f'''
                SELECT title, release_year
                FROM netflix
                WHERE release_year BETWEEN {year1} AND {year2}
                LIMIT 100
            '''
    result = []
    for item in get_value_from_db(sql=sql):
        result.append(dict(item))

    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=4),
        status=200,
        mimetype="application/json"
    )


@app.get("/rating/<rating>/")
def search_by_rating_view(rating):
    my_dict = {
        "children": ("G", "G"),
        "family": ("G", "PG", "PG-13"),
        "adult": ("R", "NC-17")
    }
    sql = f'''
                SELECT title, rating, description
                FROM netflix
                WHERE rating IN {my_dict.get(rating, ("R", "R"))}
            '''
    result = []
    for item in get_value_from_db(sql=sql):
        result.append(dict(item))

    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=4),
        status=200,
        mimetype="application/json"
    )


@app.get("/genre/<genre>/")
def search_by_genre_view(genre):
    sql = f'''
                SELECT *
                FROM netflix
                WHERE listed_in LIKE %'{genre}'
                ORDER BY release_year DESC
                LIMIT 10
            '''
    result = []
    for item in get_value_from_db(sql=sql):
        result.append(dict(item))

    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=4),
        status=200,
        mimetype="application/json"
    )


def search_by_double_name(name1, name2):
    sql = f'''
                SELECT cast
                FROM netflix
                WHERE cast LIKE %'{name1}'% AND cast LIKE %'{name2}'%
            '''
    result = []

    names_dict = {}
    for item in get_value_from_db(sql=sql):
        names = set(dict(item).get("cast").split(",")) - set([name1, name2])

        for name in names:
            names_dict[str(name).strip()] = names_dict.get(str(name).strip(), 0) + 1

    for key, value in names_dict.items():
        if value >= 2:
            result.append(key)

    return json.dumps(result, ensure_ascii=False, indent=4)


def step_6(typ, year, genre):
    sql = f'''
                SELECT title, description, listed_in
                FROM netflix
                WHERE type = '{typ}' 
                AND release_year = '{year}'
                AND listed_in LIKE '%{genre}%'
            '''
    result = []
    for item in get_value_from_db(sql):
        result.append(dict(item))

    return json.dumps(result, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True
    )
