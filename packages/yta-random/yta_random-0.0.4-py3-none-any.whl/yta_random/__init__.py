from yta_validation.parameter import ParameterValidator

import random
import string


class Random:
    """
    Class to wrap our custom random methods.
    """

    @staticmethod
    def float_between(
        start: float,
        end: float,
        step: float = 0.001
    ) -> float:
        """
        Get a random float number in between the range
        by the given 'start' and 'end' limits, using the
        also provided 'step'.

        The limits are inverted if the 'end' is lower
        than the 'start'.

        TODO: Is the limit included (?) Review and, if
        necessary, include it as a parameter.
        """
        ParameterValidator.validate_mandatory_number('start', start)
        ParameterValidator.validate_mandatory_number('end', end)
        ParameterValidator.validate_mandatory_number('step', step)
        
        start = float(start)
        end = float(end)
        step = float(step)

        # TODO: What about step = 0 or things like that (?)
        # TODO: What if 'start' and 'end' are the same (?)

        # Swap limits if needed
        start, end = (
            (end, start)
            if end < start else
            (start, end)
        )

        return random.choice(
            [
                round(start + i * step, 4)
                for i in range(int((end - start) / step) + 1)
                if start + i * step <= end
            ]
        )
    
    @staticmethod
    def int_between(
        start: int,
        end: int,
        step: int = 1 
    ) -> int:
        """
        Get a random int number in between the range
        by the given 'start' and 'end' limits, using the
        also provided 'step'.

        The limits are inverted if the 'end' is lower
        than the 'start'. The limits are included.
        """
        # TODO: What about strings that are actually parseable
        # as those numbers (?)
        ParameterValidator.validate_mandatory_int('start', start)
        ParameterValidator.validate_mandatory_int('end', end)
        ParameterValidator.validate_mandatory_int('step', step)
        
        start = int(start)
        end = int(end)
        step = int(step)

        # TODO: What about step = 0 or things like that (?)
        # TODO: What if 'start' and 'end' are the same (?)
        
        # Swap limits if needed
        start, end = (
            (end, start)
            if end < start else
            (start, end)
        )
        
        return random.randrange(start, end + 1, step)
    
    @staticmethod
    def bool(
    ) -> bool:
        """
        Get a boolean value chosen randomly.
        """
        return bool(random.getrandbits(1))

    @staticmethod
    def chance(
        probability: float = 50.0
    ) -> bool:
        """
        Get a boolean value chosen according to the
        'percentage' provided, that must be a number
        between 0 and 100, where 50 means a 50% of
        probability of getting True as the boolean
        value.

        You can provide 1/4 as parameterfor a one in
        four chance.
        """
        ParameterValidator.validate_mandatory_number_between('probability', probability, 0.0, 100.0)

        return Random.float_between(0.0, 100.0) < probability
    
    @staticmethod
    def characters(
        n: int = 10
    ) -> str:
        """
        Get a string with 'n' random characters.
        """
        return ''.join(random.choices(string.ascii_letters, k = n))
    
    @staticmethod
    def digits(
        n: int = 10
    ) -> str:
        """
        Get a string with 'n' random digits.
        """
        return ''.join(random.choices(string.digits, k = n))
    
    @staticmethod
    def characters_and_digits(
        n: int = 10
    ) -> str:
        """
        Get a string with 'n' random characters and digits.
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k = n))