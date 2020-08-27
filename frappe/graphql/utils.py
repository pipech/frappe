import graphene
import frappe

from collections import OrderedDict
from types import SimpleNamespace

from frappe.model import no_value_fields

from graphene.types.field import Field
from graphene.types.utils import yank_fields_from_attrs


frappe_graphene_map = {
    'Currency': graphene.Decimal,
    'Int': graphene.Int,
    'Long Int': graphene.Int,
    'Float': graphene.Float,
    'Percent': graphene.Float,
    'Check': graphene.Boolean,
    'Small Text': graphene.String,
    'Long Text': graphene.String,
    'Code': graphene.String,
    'Text Editor': graphene.String,
    'Markdown Editor': graphene.String,
    'HTML Editor': graphene.String,
    'Date': graphene.Date,
    'Datetime': graphene.DateTime,
    'Time': graphene.Time,
    'Text': graphene.String,
    'Data': graphene.String,
    'Link': graphene.Field,
    'Dynamic Link': graphene.String,
    'Select': graphene.String,
    'Rating': graphene.Float,
    'Read Only': graphene.String,
    'Signature': graphene.String,
    'Color': graphene.String,
    'Barcode': graphene.String,
    'Geolocation': graphene.String,
    'Attach': graphene.String,
}
frappe_not_include = [
    'Password',
    'Attach Image',
]
frappe_default_fields_type = [
    {
        'fieldname': 'name',
        'fieldtype': 'Data',
        'options': None,
    },
    {
        'fieldname': 'owner',
        'fieldtype': 'Link',
        'options': 'User',
    },
    {
        'fieldname': 'idx',
        'fieldtype': 'Int',
        'options': None,
    },
    {
        'fieldname': 'creation',
        'fieldtype': 'Datetime',
        'options': None,
    },
    {
        'fieldname': 'modified',
        'fieldtype': 'Datetime',
        'options': None,
    },
    {
        'fieldname': 'modified_by',
        'fieldtype': 'Link',
        'options': 'User',
    },
    {
        'fieldname': '_user_tags',
        'fieldtype': 'Data',
        'options': None,
    },
    {
        'fieldname': '_liked_by',
        'fieldtype': 'Data',
        'options': None,
    },
    {
        'fieldname': '_comments',
        'fieldtype': 'Data',
        'options': None,
    },
    {
        'fieldname': '_assign',
        'fieldtype': 'Text',
        'options': None,
    },
    {
        'fieldname': 'docstatus',
        'fieldtype': 'Int',
        'options': None,
    },
    {
        'fieldname': 'parent',
        'fieldtype': 'Data',
        'options': None,
    },
    {
        'fieldname': 'parentfield',
        'fieldtype': 'Data',
        'options': None,
    },
    {
        'fieldname': 'parenttype',
        'fieldtype': 'Data',
        'options': None,
    },
    {
        'fieldname': 'doctype',
        'fieldtype': 'Data',
        'options': None,
    },
]


def fetch_frappe_field(doctype):
    fields = []

    docfields = frappe.get_all(
        'DocField',
        fields=[
            'fieldname',
            'fieldtype',
            'options',
        ],
        filters={'parent': doctype}
    )
    fields.extend(docfields)

    customfield = frappe.get_all(
        'Custom Field',
        fields=[
            'fieldname',
            'fieldtype',
            'options',
        ],
        filters={'dt': doctype}
    )
    fields.extend(customfield)

    fields.extend(frappe_default_fields_type)

    return fields


def make_field_and_resolver(cls, doctype):
    frappe_fields = fetch_frappe_field(doctype)

    graphene_fields = {}
    for f in frappe_fields:
        f = SimpleNamespace(**f)
        if f.fieldtype in no_value_fields:
            continue

        if f.fieldtype == 'Link':
            # https://stackoverflow.com/questions/44312252/graphene-resolver-for-an-object-that-has-no-model
            graphene_fields[f.fieldname] = graphene.String()

            def resolver(self, info, **kwargs):
                return 'abcd'
            resolver_name = 'resolve_{}'.format(f.fieldname)
            setattr(cls, resolver_name, resolver)

        else:
            graphene_fields[f.fieldname] = frappe_graphene_map.get(
                f.fieldtype
            )()

    fields = OrderedDict()
    fields = yank_fields_from_attrs(
        graphene_fields,
        _as=Field,
    )

    return cls, fields
