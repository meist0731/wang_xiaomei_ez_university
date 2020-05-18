
from __future__ import unicode_literals
from django.db import migrations, models

import re

YEARS = [
    {
        'year': 9999,
    },

]

PERIODS = [
    {
        "period_sequence": 9999,
        "period_name": "TemporaryValue",
    },
]


def extract_year(semester_name):
    answer = re.findall(r'^\d{4} ', semester_name)
    if len(answer) != 1:
        raise ValueError('Error found in year portion of semester name:', semester_name)
    return answer[0]


def extract_period_name(semester_name):
    answer = re.findall(r' (Spring|Summer|Fall)$', semester_name)
    if len(answer) != 1:
        raise ValueError('Error found in calendar_period portion of semester name:', semester_name)
    return answer[0]


def forward_convert_semester_data(apps, schema_editor):
    year_class = apps.get_model('courseinfo', 'Year')
    period_class = apps.get_model('courseinfo', 'Period')
    semester_class = apps.get_model('courseinfo', 'Semester')

    semesters = semester_class.objects.all()
    for semester in semesters:
        this_year = extract_year(semester.semester_name)
        this_period_name = extract_period_name(semester.semester_name)

        year_object = year_class.objects.get(
            year=this_year
        )
        semester.year = year_object
        semester.save()

        period_object = period_class.objects.get(
            period_name=this_period_name
        )
        semester.period = period_object
        semester.save()


def reverse_convert_semester_data(apps, schema_editor):
    year_class = apps.get_model('courseinfo', 'Year')
    period_class = apps.get_model('courseinfo', 'Period')
    semester_class = apps.get_model('courseinfo', 'Semester')

    semesters = semester_class.objects.all()
    for semester in semesters:
        semester.semester_name = str(semester.year.year) + ' - ' + semester.period.period_name

        year_object = year_class.objects.get(
            year=9999
        )
        semester.year = year_object
        semester.save()

        period_object = period_class.objects.get(
            period_sequence=9999
        )
        semester.period = period_object
        semester.save()


def remove_calendar_period_data(apps, schema_editor):
    period_class = apps.get_model('courseinfo', 'Period')
    for this_period in PERIODS:
        period_object = period_class.objects.get(
            period_sequence=this_period['period_sequence']
        )
        period_object.delete()


def add_calendar_period_data(apps, schema_editor):
    period_class = apps.get_model('courseinfo', 'Period')
    for this_period in PERIODS:
        period_object = period_class.objects.create(
            period_sequence=this_period['period_sequence'],
            period_name=this_period['period_name']
        )


def remove_year_data(apps, schema_editor):
    year_model_class = apps.get_model('courseinfo', 'Year')
    for this_year in YEARS:
        year_object = year_model_class.objects.get(
            year=this_year['year']
        )
        year_object.delete()


def add_year_data(apps, schema_editor):
    year_model_class = apps.get_model('courseinfo', 'Year')
    for this_year in YEARS:
        year_object = year_model_class.objects.create(
            year=this_year['year']
        )


class Migration(migrations.Migration):

    dependencies = [
        ('courseinfo', '0005_year_schema_and_data'),
    ]

    operations = [

        migrations.AlterField(
            model_name='semester',
            name='semester_name',
            field=models.CharField(max_length=45, unique=False, default='temporary value'),
        ),

        migrations.AddField(
            model_name='semester',
            name='year',
            field=models.ForeignKey(to='courseinfo.year', on_delete=models.PROTECT, default=9999)
        ),

        migrations.AddField(
            model_name='semester',
            name='period',
            field=models.ForeignKey(to='courseinfo.period', on_delete=models.PROTECT, default=9999)
        ),

        migrations.RunPython(
            forward_convert_semester_data,
            reverse_convert_semester_data
        ),

        migrations.RunPython(
            remove_calendar_period_data,
            add_calendar_period_data
        ),

        migrations.RunPython(
            remove_year_data,
            add_year_data
        ),

        migrations.RemoveField(
            model_name='semester',
            name='semester_name'
        ),

        migrations.AlterField(
            model_name='semester',
            name='year',
            field=models.ForeignKey(to='courseinfo.year', on_delete=models.PROTECT)
        ),

        migrations.AlterField(
            model_name='semester',
            name='period',
            field=models.ForeignKey(to='courseinfo.period', on_delete=models.PROTECT)
        ),

        migrations.AlterUniqueTogether(
            name="semester",
            unique_together=set([('year', 'period')]),
        ),


    ]


