#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from uuid import uuid4
from random import choice
from ujson import dumps

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer

from neomodel import (
    StructuredNode, StringProperty, IntegerProperty,
    RelationshipTo, RelationshipFrom
)


class Person(StructuredNode):
    name = StringProperty(unique_index=True)
    age = IntegerProperty(index=True, default=0)

    # traverse outgoing IS_FROM relations, inflate to Country objects
    country = RelationshipTo('server.Country', 'IS_FROM')


class Country(StructuredNode):
    code = StringProperty(unique_index=True, required=True)

    # traverse incoming IS_FROM relation, inflate to Person objects
    inhabitants = RelationshipFrom(Person, 'IS_FROM')

    @classmethod
    def get_inhabitants(cls):
        country_category = Country.category()
        results, columns = country_category.cypher(
            "MATCH b-[:IS_FROM]->(a) RETURN a, count(b)"
        )
        return [(cls.inflate(row[0]), int(row[1])) for row in results]


class GetHandler(tornado.web.RequestHandler):
    def get(self):
        country_inhabitants = Country.get_inhabitants()
        countries = []
        for c, inhabitants in country_inhabitants:
            countries.append(dict(
                code=c.code,
                inhabitants=inhabitants
            ))
        self.write(dumps(countries))


class PostHandler(tornado.web.RequestHandler):
    def post(self):
        users = []

        for i in range(400):
            uid = uuid4()
            users.append(dict(
                name='User-%s' % uid,
                age=30
            ))

        people = Person.create(*users)

        countries = []
        for i in range(100):
            uid = uuid4()
            countries.append(dict(
                code="country-%s" % uid
            ))

        countries = Country.create(*countries)

        for person in people:
            person.country.connect(choice(countries))

        self.write('%d people created in %d countries' % (
            len(people), len(countries)
        ))


def main():
    os.environ['NEO4J_REST_URL'] = 'http://localhost:7474/db/data/'
    routes = [
        ('/get', GetHandler),
        ('/post', PostHandler),
    ]

    application = tornado.web.Application(routes, debug=True)
    server = HTTPServer(application)
    server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
