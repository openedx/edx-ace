from django.test import TestCase
from edx_ace.utils.signals import make_serializable_object


class TestMakeSerializableObject(TestCase):
    def test_primitive_types(self):
        self.assertEqual(make_serializable_object(42), 42)
        self.assertEqual(make_serializable_object(3.14), 3.14)
        self.assertEqual(make_serializable_object("string"), "string")
        self.assertEqual(make_serializable_object(True), True)
        self.assertEqual(make_serializable_object(None), None)

    def test_dict(self):
        input_dict = {
            "int": 1,
            "float": 2.0,
            "str": "test",
            "bool": False,
            "none": None,
            "list": [1, 2, 3],
            "nested_dict": {"key": "value"}
        }
        self.assertEqual(make_serializable_object(input_dict), input_dict)

    def test_list(self):
        input_list = [1, 2.0, "test", False, None, [1, 2, 3], {"key": "value"}]
        self.assertEqual(make_serializable_object(input_list), input_list)

    def test_non_serializable(self):
        class NonSerializable:
            pass

        obj = NonSerializable()
        self.assertEqual(make_serializable_object(obj), str(obj))

    def test_non_serializable_list(self):
        class NonSerializable:
            pass

        obj = NonSerializable()
        obj2 = NonSerializable()
        obj_list = [obj, obj2]
        self.assertEqual(make_serializable_object(obj_list), [str(obj), str(obj2)])
