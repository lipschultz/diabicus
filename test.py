import unittest
import math

import calculator

from src import compute
from src import numeric_tools
from src import simpleeval
from src import format_numbers

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

    @unittest.skip("simpleeval thinks it'll take too long to compute")
    def test_large_root(self):
        self.assign_value_to_Ans(1.668e14)
        self.enter_basic_input('^.5')
        self.app.press_ans()
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, 12915107.432770353)

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

    def test_pi_results_in_pi_value(self):
        self.enter_basic_input('π')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, math.pi)

    def test_e_results_in_e_value(self):
        self.enter_basic_input('e')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, math.e)

    def test_phi_results_in_phi_value(self):
        self.enter_basic_input('φ')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, numeric_tools.GOLDEN_RATIO)

    def test_i_results_in_i_value(self):
        self.enter_basic_input('i')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, numeric_tools.I)

    def test_tau_results_in_tau_value(self):
        self.enter_basic_input('τ')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, 2*math.pi)

    def test_implicit_multiply_Ans_pi(self):
        self.assign_value_to_Ans(3)
        self.app.press_ans()
        self.enter_basic_input('π')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, 9.42477796076938)

    def test_implicit_multiply_pi_e(self):
        self.enter_basic_input('π')
        self.enter_basic_input('e')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, 8.539734222673566)

    def test_implicit_multiply_pi_e_phi(self):
        self.enter_basic_input('π')
        self.enter_basic_input('e')
        self.enter_basic_input('φ')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, 13.817580227176492)

    def test_implicit_multiply_e_i_tau(self):
        self.enter_basic_input('e')
        self.enter_basic_input('i')
        self.enter_basic_input('τ')
        self.app.calculate()
        self.assertAlmostEqual(self.app.result, complex(0, 17.079468445347132))

    def test_context_stores_past_results(self):
        self.enter_basic_input('2+2')
        self.app.calculate()
        self.enter_basic_input('9/3')
        self.app.calculate()
        context = self.app.get_context()
        self.assertEqual(context['formula'], ['2+2', '9/3'])
        self.assertEqual(context['result'], [4, 3.0])

class ComputeTests(unittest.TestCase):
    def setUp(self):
        self.eval = simpleeval.SimpleEval()

    def test_catches_divide_by_zero_and_returns_appropriate_error(self):
        result = compute.eval_expr(self.eval, '5/0')
        self.assertIsInstance(result, compute.ComputationError)
        self.assertEqual(result.msg, 'divide by zero')

class FormatNumbersTests(unittest.TestCase):
    ANY_VALUE_ABOVE_THRESHOLD = 5

    def test_simplifying_complex_removes_real_below_threshold(self):
        num = complex(1e-17, self.ANY_VALUE_ABOVE_THRESHOLD)
        snum = format_numbers.simplify_complex(num, 1e-15, 1e-15)
        self.assertEqual(snum, complex(0, self.ANY_VALUE_ABOVE_THRESHOLD))

    def test_simplifying_complex_removes_imag_below_threshold(self):
        num = complex(self.ANY_VALUE_ABOVE_THRESHOLD, 1e-17)
        snum = format_numbers.simplify_complex(num, 1e-18, 1e-15)
        self.assertEqual(snum, complex(self.ANY_VALUE_ABOVE_THRESHOLD, 0))

    def test_simplifying_complex_uses_real_threshold_default(self):
        num = complex(0.1e-16, self.ANY_VALUE_ABOVE_THRESHOLD)
        snum = format_numbers.simplify_complex(num)
        self.assertEqual(snum, complex(0, self.ANY_VALUE_ABOVE_THRESHOLD))

    def test_simplifying_complex_imag_threshold_defaults_to_real_threshold(self):
        num = complex(self.ANY_VALUE_ABOVE_THRESHOLD, 0.1e-16)
        snum = format_numbers.simplify_complex(num)
        self.assertEqual(snum, complex(self.ANY_VALUE_ABOVE_THRESHOLD, 0))

    def test_simplifying_complex_returns_zero_if_both_below_threshold(self):
        num = complex(0.1e-16, 0.1e-16)
        snum = format_numbers.simplify_complex(num)
        self.assertEqual(snum, 0)

    def test_simplifying_complex_returns_original_number_if_both_above_threshold(self):
        num = complex(self.ANY_VALUE_ABOVE_THRESHOLD, self.ANY_VALUE_ABOVE_THRESHOLD)
        snum = format_numbers.simplify_complex(num)
        self.assertEqual(snum, num)

    def test_simplifying_complex_absolute_value_used_when_comparing_real(self):
        num = complex(-self.ANY_VALUE_ABOVE_THRESHOLD, self.ANY_VALUE_ABOVE_THRESHOLD)
        snum = format_numbers.simplify_complex(num)
        self.assertEqual(snum, num)

    def test_simplifying_complex_absolute_value_used_when_comparing_imag(self):
        num = complex(self.ANY_VALUE_ABOVE_THRESHOLD, -self.ANY_VALUE_ABOVE_THRESHOLD)
        snum = format_numbers.simplify_complex(num)
        self.assertEqual(snum, num)

    def test_prettying_ints_larger_than_can_fit_in_float(self):
        num = 2**(36862)+1
        pnum = format_numbers.to_pretty_x10(num)
        self.assertEqual(pnum, '3.69573×10^11096')

    def test_prettying_num_needing_negative_exponent(self):
        num = 0.000000000000016007448567456
        pnum = format_numbers.to_pretty_x10(num)
        self.assertEqual(pnum, '1.60074×10^-14')

    def test_prettying_num_that_shouldnt_become_sci_notation(self):
        num = 0.16007448567456
        pnum = format_numbers.to_pretty_x10(num)
        self.assertEqual(pnum, '0.16007')


if __name__ == '__main__':
    unittest.main()
