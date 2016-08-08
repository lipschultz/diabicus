import unittest
import calculator
import compute

class CalculatorTests(unittest.TestCase):
    def setUp(self):
        self.app = calculator.Calculator()

    def enter_basic_input(self, text):
        for c in text:
            self.app.press_key(c)

    def assign_value_to_Ans(self, value):
        self.enter_basic_input(str(value))
        self.app.calculate()

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

    def test_typing_after_calculate_clears_input(self):
        self.enter_basic_input('1234+6789')
        self.app.calculate()
        self.enter_basic_input('50')
        self.assertEqual(self.app.input, '50')

    def test_output_matches_result(self):
        self.enter_basic_input('12345+67890')
        self.app.calculate()
        self.assertEqual(self.app.output, str(self.app.result))

    def test_basic_arithmetic(self):
        self.enter_basic_input('3-5×2+9/3^2')
        self.app.calculate()
        self.assertEqual(self.app.result, -6)

    def test_implicit_multiplication_num_paren(self):
        self.enter_basic_input('3(2-5)')
        self.app.calculate()
        self.assertEqual(self.app.result, -9)

    def test_implicit_multiplication_paren_num(self):
        self.enter_basic_input('(2-5)3')
        self.app.calculate()
        self.assertEqual(self.app.result, -9)

    def test_implicit_multiplication_using_parentheses_preceded_by_decimal_point(self):
        self.enter_basic_input('3.(2-5)')
        self.app.calculate()
        self.assertEqual(self.app.result, -9)

    def test_implicit_multiplication_parentheses_time_parentheses(self):
        self.enter_basic_input('(3-1)(2-5)')
        self.app.calculate()
        self.assertEqual(self.app.result, -6)

    def test_typing_ans_inputs_Ans(self):
        self.app.press_ans()
        self.assertEqual(self.app.input, "Ans")

    def test_Ans_initialized_to_zero(self):
        self.app.press_ans()
        self.app.calculate()
        self.assertEqual(self.app.result, 0)

    def test_Ans_value_updated_after_calculation(self):
        self.enter_basic_input('12345+67890')
        self.app.calculate()
        self.app.press_ans()
        self.app.calculate()
        self.assertEqual(self.app.output, '80235')

    def test_Ans_value_unchanged_after_error(self):
        self.enter_basic_input('12345*/^*')
        self.app.calculate()
        self.app.press_ans()
        self.app.calculate()
        self.assertEqual(self.app.output, '0')

    def test_bksp_deletes_one_char_to_the_left_of_cursor(self):
        self.enter_basic_input('123')
        self.app.bksp()
        self.assertEqual(self.app.input, '12')

    def test_bksp_on_empty_input(self):
        self.app.bksp()
        self.assertEqual(self.app.input, '')

    def test_bksp_on_Ans_deletes_Ans(self):
        self.app.press_ans()
        self.app.bksp()
        self.assertEqual(self.app.input, '')

    def test_bksp_after_calculate_deletes_input_char(self):
        self.enter_basic_input('123')
        self.app.calculate()
        self.app.bksp()
        self.assertEqual(self.app.input, '12')

    def test_calculate_bksp_then_type_adds_to_input(self):
        self.enter_basic_input('125')
        self.app.calculate()
        self.app.bksp()
        self.enter_basic_input('3')
        self.assertEqual(self.app.input, '123')

    def test_start_with_non_plus_minus_operator_prepends_Ans(self):
        self.enter_basic_input('×2')
        self.assertEqual(self.app.input, 'Ans×2')

    def test_start_with_plus_operator_does_not_prepend_Ans(self):
        self.enter_basic_input('+2')
        self.assertEqual(self.app.input, '+2')

    def test_start_with_minus_operator_does_not_prepend_Ans(self):
        self.enter_basic_input('-2')
        self.assertEqual(self.app.input, '-2')

    def test_func_typed(self):
        self.app.press_function_key('ln')
        self.assertEqual(self.app.input, compute.FUNCTION_PREFIX + 'ln(')

    def test_func_evaluated_correctly(self):
        self.app.press_function_key('ln')
        self.enter_basic_input('2)')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, 0.6931471805599453)

    def test_func_after_calc_clears_input(self):
        self.enter_basic_input('12345+67890')
        self.app.calculate()
        self.app.press_function_key('ln')
        self.assertEqual(self.app.input, compute.FUNCTION_PREFIX + 'ln(')

    def test_bksp_deletes_full_func_name(self):
        self.app.press_function_key('ln')
        self.app.bksp()
        self.assertEqual(self.app.input, '')

    def test_bksp_deletes_opening_paren_at_start_of_input(self):
        self.enter_basic_input('(')
        self.app.bksp()
        self.assertEqual(self.app.input, '')

    def test_bksp_deletes_only_opening_paren_when_input_starts_with_digit_open_paren(self):
        self.enter_basic_input('2(')
        self.app.bksp()
        self.assertEqual(self.app.input, '2')

    def test_implicit_multiply_number_func_name(self):
        self.enter_basic_input('2')
        self.app.press_function_key('ln')
        self.enter_basic_input('2)')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, 1.3862943611198906)

    def test_implicit_multiply_func_number(self):
        self.app.press_function_key('ln')
        self.enter_basic_input('2)2')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, 1.3862943611198906)

    def test_implicit_multiply_func_func(self):
        self.app.press_function_key('ln')
        self.enter_basic_input('2)')
        self.app.press_function_key('ln')
        self.enter_basic_input('2)')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, 0.4804530139182014)

    def test_implicit_multiply_Ans_func_name(self):
        self.assign_value_to_Ans(2)
        self.app.press_ans()
        self.app.press_function_key('ln')
        self.enter_basic_input('2)')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, 1.3862943611198906)

    def test_implicit_multiply_func_Ans(self):
        self.assign_value_to_Ans(2)
        self.app.press_function_key('ln')
        self.enter_basic_input('2)')
        self.app.press_ans()
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, 1.3862943611198906)

    def test_implicit_multiply_num_Ans(self):
        self.assign_value_to_Ans(3)
        self.enter_basic_input('2')
        self.app.press_ans()
        self.app.calculate()
        self.assertEqual(self.app.result, 6)

    def test_implicit_multiply_Ans_num(self):
        self.assign_value_to_Ans(3)
        self.app.press_ans()
        self.enter_basic_input('2')
        self.app.calculate()
        self.assertEqual(self.app.result, 6)

    def test_implicit_multiply_Ans_Ans(self):
        self.assign_value_to_Ans(3)
        self.app.press_ans()
        self.app.press_ans()
        self.app.calculate()
        self.assertEqual(self.app.result, 9)

if __name__ == '__main__':
    unittest.main()
