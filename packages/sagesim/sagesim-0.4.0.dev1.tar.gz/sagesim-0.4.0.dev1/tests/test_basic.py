import unittest
import sagesim
import sagesim.breed

class TestSAGESimBasic(unittest.TestCase):
    def test_version(self):
        # Check if sagesim has a __version__ attribute
        self.assertTrue(hasattr(sagesim, '__version__'))

    def test_basics(self):
        model = sagesim.Model()
        breed_predator = sagesim.breed.Breed('predator')
        breed_predator
        breed_prey = sagesim.breed.Breed('prey')

        model.register_breed(breed_predator)
        model.register_breed(breed_prey)


        

if __name__ == '__main__':
    unittest.main()