import unittest
from assemtobinary import main
from utils import values_prepare


class TestAssemble(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def test_main(self):
        expected_values = values_prepare()
        
        values = main("./test.S")
        
        self.assertListEqual(values, expected_values)
        
        # self.assertEqual(values, expected_values)
        
if __name__ == "__main__":
    # print(preparar_valores())
    unittest.main()