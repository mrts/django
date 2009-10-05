"""
Raw overrides provide a way to insert complex raw SQL not supported by the
ORM into parts the query.

As of now, only ORDER BY overrides are supported.
"""

from django.db import models

class Word(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s. %s" % (self.pk, self.name)

class CourseDate(models.Model):
    course = models.ForeignKey(Course)
    start = models.DateField()
    end = models.DateField()

__test__ = {'API_TESTS':"""
Create some words.

>>> w1 = Word(name="short")
>>> w1.save()
>>> w2 = Word(name="sabotage")
>>> w2.save()
>>> w3 = Word(name="subtle")
>>> w3.save()
>>> w4 = Word(name="submarine")
>>> w4.save()
>>> w5 = Word(name="obnoxious")
>>> w5.save()
>>> w6 = Word(name="affluent")
>>> w6.save()

>>> Word.objects.filter(name__startswith="s").order_by('name')
[<Word: sabotage>, <Word: short>, <Word: submarine>, <Word: subtle>]

Order words by their length. Filtering and raw_override() should work well
together.

>>> Word.objects.filter(name__startswith="s")\
        .raw_override(order_by='LENGTH("name")')
[<Word: short>, <Word: subtle>, <Word: sabotage>, <Word: submarine>]
>>> Word.objects.raw_override(order_by='LENGTH("name")')\
        .filter(name__startswith="s")
[<Word: short>, <Word: subtle>, <Word: sabotage>, <Word: submarine>]

raw_override() always overrides order_by().

>>> Word.objects.filter(name__startswith="s")\
        .order_by('name')\
        .raw_override(order_by='LENGTH("name")')
[<Word: short>, <Word: subtle>, <Word: sabotage>, <Word: submarine>]
>>> Word.objects.filter(name__startswith="s")\
        .raw_override(order_by='LENGTH("name")')\
        .order_by('name')
[<Word: short>, <Word: subtle>, <Word: sabotage>, <Word: submarine>]

A more complex and somewhat realistic example that uses joins and CASE in
ordering. Also, demonstrates that order_by_params work as expected.

Imagine that you manage courses and want them listed in order of "immediacy"
after a given date, i.e. the ones that either end or start near that date are
of greatest interest. An example in raw SQL (the `order_date` and `which`
CASES in SELECT are for clarity):

SELECT c.name, cd.start,
  (CASE WHEN cd.start < '2009-10-05'
	THEN cd.end ELSE cd.start END) as order_date,
  (CASE WHEN cd.start < '2009-10-05' THEN 'end' ELSE 'start' END) as which
   FROM courses_course c
     INNER JOIN courses_coursedate cd
       ON c.id = cd.course_id
   WHERE cd.end >= '2009-10-05'
   ORDER BY (CASE WHEN cd.start < '2009-10-05' THEN cd.end ELSE cd.start END)
       ASC;

               name                |   start    | order_date | which
-----------------------------------+------------+------------+-------
 Kung-foo for desperate housewives | 2009-10-05 | 2009-10-05 | start
 Kung-foo for Python developers    | 2009-10-04 | 2009-10-07 | end
 Kung-foo for desperate housewives | 2009-10-10 | 2009-10-10 | start
 Kung-foo for beginners            | 2009-10-26 | 2009-10-26 | start
 Kung-foo for beginners            | 2009-09-26 | 2009-10-30 | end

>>> from datetime import date

>>> c1 = Course(name="Kung-foo for beginners")
>>> c1.save()
>>> c1d1 = CourseDate(course=c1, start=date(2009, 9, 26),
... end=date(2009, 10, 30))
>>> c1d1.save()
>>> c1d2 = CourseDate(course=c1, start=date(2009, 10, 26),
... end=date(2009, 10, 30))
>>> c1d2.save()

>>> c2 = Course(name="Kung-foo for Python developers")
>>> c2.save()
>>> c2d1 = CourseDate(course=c2, start=date(2009, 10, 1),
... end=date(2009, 10, 4))
>>> c2d1.save()
>>> c2d2 = CourseDate(course=c2, start=date(2009, 10, 4),
... end=date(2009, 10, 7))
>>> c2d2.save()

>>> c3 = Course(name="Kung-foo for desperate housewives")
>>> c3.save()
>>> c3d1 = CourseDate(course=c3, start=date(2009, 10, 5),
... end=date(2009, 10, 7))
>>> c3d1.save()
>>> c3d2 = CourseDate(course=c3, start=date(2009, 10, 10),
... end=date(2009, 10, 12))
>>> c3d2.save()

>>> the_date = date(2009, 10, 5)
>>> RAW_ORDER_BY = '''(CASE WHEN "raw_override_coursedate"."start" < %s
... THEN "raw_override_coursedate"."end"
... ELSE "raw_override_coursedate"."start" END) ASC'''

Ordinary order:

>>> Course.objects.filter(coursedate__end__gte=the_date)\
        .order_by('coursedate__start')
[<Course: 1. Kung-foo for beginners>, <Course: 2. Kung-foo for Python developers>, <Course: 3. Kung-foo for desperate housewives>, <Course: 3. Kung-foo for desperate housewives>, <Course: 1. Kung-foo for beginners>]

Desired order:

>>> Course.objects.filter(coursedate__end__gte=the_date)\
        .raw_override(order_by=RAW_ORDER_BY,
...         order_by_params=(the_date,))
[<Course: 3. Kung-foo for desperate housewives>, <Course: 2. Kung-foo for Python developers>, <Course: 3. Kung-foo for desperate housewives>, <Course: 1. Kung-foo for beginners>, <Course: 1. Kung-foo for beginners>]
"""}
