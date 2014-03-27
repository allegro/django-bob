# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from mock import Mock

from django.test import TestCase
from django.db.models import Model

from bob.forms.dependency_conditions import (
    first_letter_lower,
    format_single_val_for_js,
    format_val_for_js,
    Any,
    Exact,
    MemberOf,
    NotEmpty,
)


class FirstLetterLowerTest(TestCase):
    def test_lower(self):
        self.assertEqual(first_letter_lower("abcdefgh"), "abcdefgh")
        self.assertEqual(first_letter_lower("a a a a"), "a a a a")

    def test_upper(self):
        self.assertEqual(first_letter_lower("AbDe3fd#EDFG"), "abDe3fd#EDFG")
        self.assertEqual(first_letter_lower("A a a a"), "a a a a")

    def test_real(self):
        self.assertEqual(first_letter_lower("Exact"), "exact")
        self.assertEqual(first_letter_lower("MemberOf"), "memberOf")
        self.assertEqual(first_letter_lower("NotEmpty"), "notEmpty")


class FormatSingleValForJsTest(TestCase):
    def test_bool(self):
        self.assertEqual(format_single_val_for_js(True), True)
        self.assertEqual(format_single_val_for_js(False), False)

    def test_none(self):
        self.assertEqual(format_single_val_for_js(None), None)

    def test_not_string(self):
        self.assertEqual(format_single_val_for_js("123"), "123")

    def test_date(self):
        dt = date(2012, 04, 15)
        self.assertEqual(format_single_val_for_js(dt), "2012-04-15")

    def test_model(self):
        model = Mock(spec=Model)
        model.pk = "321"
        self.assertEqual(format_single_val_for_js(model), "321")


class FormatValForJsTest(TestCase):
    def test_single_string(self):
        self.assertEqual(format_val_for_js("abcdefgh22"), "abcdefgh22")
        self.assertEqual(format_val_for_js("Pokoijiuh"), "Pokoijiuh")

    def test_single_bool(self):
        self.assertEqual(format_single_val_for_js(True), True)
        self.assertEqual(format_single_val_for_js(False), False)

    def test_simple_list(self):
        self.assertEqual(
            format_val_for_js([True, "456", None, 123]),
            [True, "456", None, "123"],
        )

    def test_list_with_date(self):
        dt = date(2012, 04, 15)
        self.assertEqual(
            format_val_for_js([True, "456", dt, 123]),
            [True, "456", "2012-04-15", "123"],
        )

    def test_list_with_model(self):
        model = Mock(spec=Model)
        model.pk = "321"
        self.assertEqual(
            format_val_for_js([1, "2", model]),
            ["1", "2", "321"],
        )


class AnyTest(TestCase):
    def test_python_condition(self):
        any_condition = Any()
        self.assertTrue(any_condition.met("sdf"))
        self.assertTrue(any_condition.met(False))
        self.assertTrue(any_condition.met(3))
        self.assertTrue(any_condition.met(date(2005, 10, 03)))
        self.assertTrue(any_condition.met(None))
        self.assertTrue(any_condition.met(""))

    def test_js_format_simple(self):
        any_condition = Any()
        self.assertEqual(any_condition.get_js_format(), ["any"])


class ExactTest(TestCase):
    def test_python_condition(self):
        exact = Exact(5)
        self.assertTrue(exact.met(5))
        self.assertTrue(exact.met("5"))
        self.assertFalse(exact.met(7))
        self.assertFalse(exact.met("3"))

    def test_python_condition_date(self):
        exact = Exact(date(2100, 10, 5))
        self.assertTrue(exact.met("2100-10-05"))
        self.assertTrue(exact.met(date(2100, 10, 5)))
        self.assertFalse(exact.met("2100-11-05"))
        self.assertFalse(exact.met(date(2000, 4, 18)))

    def test_python_condition_model(self):
        model_mock = Mock(spec=Model)
        model_mock.pk = 129
        model_mock_2 = Mock(spec=Model)
        model_mock_2.pk = 55
        exact = Exact(model_mock)
        self.assertTrue(exact.met(model_mock))
        self.assertTrue(exact.met("129"))
        self.assertTrue(exact.met(129))
        self.assertFalse(exact.met(model_mock_2))
        self.assertFalse(exact.met("185"))
        self.assertFalse(exact.met(19))

    def test_js_format_simple(self):
        exact = Exact(10)
        self.assertEqual(exact.get_js_format(), ["exact", "10"])

    def test_js_format_date(self):
        exact = Exact(date(2000, 01, 01))
        self.assertEqual(exact.get_js_format(), ["exact", "2000-01-01"])


class MemberOfTest(TestCase):
    def test_python_condition(self):
        memberOf = MemberOf([1, 2, 5, date(2010, 03, 19)])
        self.assertTrue(memberOf.met("2"))
        self.assertTrue(memberOf.met(5))
        self.assertFalse(memberOf.met(3))
        self.assertFalse(memberOf.met(None))

    def test_python_condition_date(self):
        memberOf = MemberOf([1, date(2010, 03, 19), 5])
        self.assertTrue(memberOf.met("2010-03-19"))
        self.assertTrue(memberOf.met(date(2010, 03, 19)))
        self.assertFalse(memberOf.met("2010-03-18"))
        self.assertFalse(memberOf.met(date(2010, 02, 19)))

    def test_python_condition_model(self):
        model_mock = Mock(spec=Model)
        model_mock.pk = 129
        exact = Exact(model_mock)
        self.assertTrue(exact.met(model_mock))
        self.assertTrue(exact.met("129"))
        self.assertTrue(exact.met(129))

    def test_js_format_simple(self):
        memberOf = MemberOf([1, True, "3"])
        self.assertEqual(
            memberOf.get_js_format(), ["memberOf", ["1", True, "3"]]
        )

    def test_js_format_date(self):
        memberOf = MemberOf([1, date(2010, 02, 19), "3"])
        self.assertEqual(
            memberOf.get_js_format(), ["memberOf", ["1", "2010-02-19", "3"]]
        )

    def test_js_format_model(self):
        model_mock = Mock(spec=Model)
        model_mock.pk = 129
        memberOf = MemberOf([True, model_mock, 0])
        self.assertEqual(
            memberOf.get_js_format(), ["memberOf", [True, "129", "0"]]
        )


class NotEmptyTest(TestCase):
    def test_python_condition(self):
        notEmpty = NotEmpty()
        self.assertTrue(notEmpty.met("srlktmgsrltkgm"))
        self.assertTrue(notEmpty.met(False))
        self.assertFalse(notEmpty.met(None))
        self.assertFalse(notEmpty.met(""))

    def test_js_format_simple(self):
        notEmpty = NotEmpty()
        self.assertEqual(
            notEmpty.get_js_format(), ["notEmpty"]
        )
