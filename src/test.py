import unittest
import calculator

class CalculatorTests(unittest.TestCase):
    def setUp(self):
        print('setting up')
        self.app = calculator.Calculator()

    def enter_basic_input(self, text):
        for c in text:
            self.app.press_key(c)

    def test_digits_input_correctly(self):
        self.enter_basic_input('1234567890')
        self.assertEqual(self.app.input, '1234567890')

    def test_clear_after_enter_input_before_equals_clears_input(self):
        self.enter_basic_input('1234567890')
        self.app.clear()
        self.assertEqual(self.app.input, '')

    def test_clear_on_empty_input(self):
        self.app.clear()
        self.assertEqual(self.app.input, '')
        self.assertEqual(self.app.output, '')

    def test_clear_after_equal_clears_only_input(self):
        self.enter_basic_input('12345+67890')
        self.app.calculate()
        self.app.clear()
        self.assertEqual(self.app.input, '')
        self.assertEqual(self.app.output, '80235')

    def test_clear_twice_after_equal_clears_input_output(self):
        self.enter_basic_input('12345+67890')
        self.app.calculate()
        self.app.clear()
        self.app.clear()
        self.assertEqual(self.app.input, '')
        self.assertEqual(self.app.output, '')

    def test_output_matches_result(self):
        self.enter_basic_input('12345+67890')
        self.app.calculate()
        self.assertEqual(self.app.output, str(self.app.result))

    def test_basic_arithmetic(self):
        self.enter_basic_input('3-5×2+9/3^2')
        self.app.calculate()
        self.assertEqual(self.app.result, -6)

    def test_implicit_multiplication_using_parentheses(self):
        self.enter_basic_input('3(2-5)')
        self.app.calculate()
        self.assertEqual(self.app.result, -9)

if __name__ == '__main__':
    unittest.main()
