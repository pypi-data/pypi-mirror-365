import numpy as np
import unittest

from trainstation import Optimizer


class TestOptimizer(unittest.TestCase):
    """Unittest class for Optimizer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.n_rows = 200
        self.n_cols = 50
        self.tol = 1.0 / self.n_rows

        # set up dummy linear problem data
        self.A = np.random.normal(0, 1, (self.n_rows, self.n_cols))
        self.x = np.random.normal(0, 5, (self.n_cols, ))
        self.noise = np.random.normal(0, 0.1, (self.n_rows, ))
        self.y = np.dot(self.A, self.x) + self.noise

    def shortDescription(self):
        """Prevents unittest from printing docstring in test cases."""
        return None

    def test_get_rows_via_sizes(self):
        """Tests _get_rows_via_sizes functionality."""

        opt = Optimizer((self.A, self.y))

        # test with only train_size defined
        train_size, test_size = int(0.8 * self.n_rows), None
        train_set, test_set = opt._get_rows_via_sizes(train_size, test_size)
        self.assertEqual(train_size, len(train_set))
        self.assertEqual(self.n_rows - train_size, len(test_set))

        # test with only test_size defined
        train_size, test_size = None, int(0.8 * self.n_rows)
        train_set, test_set = opt._get_rows_via_sizes(train_size, test_size)
        self.assertEqual(test_size, len(test_set))
        self.assertEqual(self.n_rows - test_size, len(train_set))

        # test with both defined
        train_size, test_size = int(0.8 * self.n_rows), int(0.15 * self.n_rows)
        train_set, test_set = opt._get_rows_via_sizes(train_size, test_size)
        self.assertEqual(train_size, len(train_set))
        self.assertEqual(test_size, len(test_set))

        # test with fractions
        train_size, test_size = 0.7, 0.2
        train_set, test_set = opt._get_rows_via_sizes(train_size, test_size)
        self.assertLess(abs(train_size*self.n_rows - len(train_set)), self.tol)
        self.assertLess(abs(test_size*self.n_rows - len(test_set)), self.tol)

        # test edge case with full training set
        test_size = None
        for train_size in [1.0, self.n_rows]:
            train_set, test_set = opt._get_rows_via_sizes(
                train_size, test_size)
            self.assertEqual(len(train_set), self.n_rows)
            self.assertIsNone(test_set)

        # test invalid sizes
        with self.assertRaises(ValueError):
            train_size, test_size = None, 1.0
            opt._get_rows_via_sizes(train_size, test_size)
        with self.assertRaises(ValueError):
            train_size, test_size = None, None
            opt._get_rows_via_sizes(train_size, test_size)

    def test_get_rows_from_indices(self):
        """Tests _get_rows_from_indices."""
        opt = Optimizer((self.A, self.y))
        all_rows = np.arange(self.n_rows)

        train_size = int(0.8 * self.n_rows)
        train_set_target = np.random.choice(
            all_rows, train_size, replace=False)
        test_set_target = sorted(np.setdiff1d(all_rows, train_set_target))

        # specify only train_set, test set should default to remaining rows
        train_set, test_set = opt._get_rows_from_indices(
            train_set_target, None)
        self.assertSequenceEqual(sorted(train_set_target), sorted(train_set))
        self.assertSequenceEqual(sorted(test_set_target), sorted(test_set))

        # specify only test_set, train set should default to remaining rows
        train_set, test_set = opt._get_rows_from_indices(None, test_set_target)
        self.assertSequenceEqual(sorted(train_set_target), sorted(train_set))
        self.assertSequenceEqual(sorted(test_set_target), sorted(test_set))

        # specify partial sets meaning not all rows are used
        train_set_target = np.delete(train_set_target, [0, 1, 2])
        test_set_target = np.delete(test_set_target, [0, 1, 2])
        train_set, test_set = opt._get_rows_from_indices(
            train_set_target, test_set_target)
        self.assertSequenceEqual(sorted(train_set_target), sorted(train_set))
        self.assertSequenceEqual(sorted(test_set_target), sorted(test_set))

        # test invalid input
        with self.assertRaises(ValueError):
            opt._get_rows_from_indices(None, None)

    def test_setup_rows(self):
        """
        Tests _setup_rows.

        Simply test that function raise when no training data available
        """
        opt = Optimizer((self.A, self.y))

        # no training data from train_size
        with self.assertRaises(ValueError):
            train_size, test_size = 0, 0.5
            opt._setup_rows(train_size, test_size, None, None)

        # no training data from train_set
        with self.assertRaises(ValueError):
            train_set, test_set = [], np.arange(0, int(0.5*self.n_rows))
            opt._setup_rows(None, None, train_set, test_set)

        # overlapping indices in train_set and test_set
        with self.assertRaises(ValueError):
            train_set, test_set = [1, 2, 3, 4, 5], [5, 6, 7, 8, 9, 10]
            opt._setup_rows(None, None, train_set, test_set)

    def test_train(self):
        """Tests train."""

        # with test set
        train_size = 0.75
        opt = Optimizer((self.A, self.y), train_size=train_size)
        self.assertIsNone(opt.rmse_train)
        self.assertIsNone(opt.rmse_test)
        self.assertIsNone(opt.AIC)
        self.assertIsNone(opt.BIC)
        self.assertIsNone(opt.scatter_data_train)
        self.assertIsNone(opt.scatter_data_test)
        opt.train()
        self.assertIsNotNone(opt.rmse_train)
        self.assertIsNotNone(opt.rmse_test)
        self.assertIsNotNone(opt.AIC)
        self.assertIsNotNone(opt.BIC)
        self.assertIsNotNone(opt.scatter_data_train)
        self.assertIsNotNone(opt.scatter_data_test)

        # without testing
        train_size = 1.0
        opt = Optimizer((self.A, self.y), train_size=train_size)
        self.assertIsNone(opt.rmse_train)
        self.assertIsNone(opt.rmse_test)
        self.assertIsNone(opt.scatter_data_train)
        self.assertIsNone(opt.scatter_data_test)
        opt.train()
        self.assertIsNotNone(opt.rmse_train)
        self.assertIsNone(opt.rmse_test)
        self.assertIsNotNone(opt.scatter_data_train)
        self.assertIsNone(opt.scatter_data_test)

    def test_summary_property(self):
        """Tests summary property."""

        # without having trained
        opt = Optimizer((self.A, self.y))
        self.assertIsInstance(opt.summary, dict)

        # with having trained
        opt.train()
        self.assertIsInstance(opt.summary, dict)
        self.assertIn('rmse_train', opt.summary.keys())
        self.assertIn('rmse_test', opt.summary.keys())

    def test_repr(self):
        """Tests repr dunder."""
        opt = Optimizer((self.A, self.y))
        self.assertIsInstance(repr(opt), str)

    def test_size_properties(self):
        """Tests the properties in regards to training/test sets and sizes."""

        # test without test_set
        train_set = np.arange(0, self.n_rows)
        opt = Optimizer((self.A, self.y), train_set=train_set)
        self.assertSequenceEqual(opt.train_set.tolist(), train_set.tolist())
        self.assertEqual(len(train_set), opt.train_size)
        self.assertEqual(1.0, opt.train_fraction)
        self.assertIsNone(opt.test_set)
        self.assertEqual(opt.test_size, 0)
        self.assertEqual(opt.test_fraction, 0)

        # test with test set
        test_set = np.arange(int(0.7 * self.n_rows), int(0.8 * self.n_rows))
        opt = Optimizer((self.A, self.y), test_set=test_set)
        self.assertSequenceEqual(test_set.tolist(), opt.test_set.tolist())
        self.assertEqual(opt.test_size, len(test_set))
        self.assertAlmostEqual(opt.test_fraction, len(test_set) / self.n_rows)

    def test_zero_error_with_least_square_fit(self):
        """ Test that the error is zero if training without noise and with
        least-squares. """

        # set up dummy linear problem data
        for standardize in [True, False]:
            y = np.dot(self.A, self.x)
            opt = Optimizer((self.A, y), fit_method='least-squares', standardize=standardize)
            opt.train()

            self.assertAlmostEqual(opt.rmse_train, 0.0)
            self.assertAlmostEqual(opt.rmse_test, 0.0)

            self.assertAlmostEqual(np.abs(self.x - opt.parameters).max(), 0)

    def test_model_metrics(self):
        """ Test that we get correct metrics for a trained model """

        # construct deterministic dataset
        N, M = 20, 10

        A = np.arange(N * M).reshape((N, M)).astype(float)
        for i in range(N):
            A[i, :] = (A[i, :] / np.arange(i+2, i+2+M))
        A = np.mod(A, 0.9)

        x = np.arange(M) / M
        noise = 0.5 / np.arange(1, N+1)
        y = np.dot(A, x) + noise

        # train
        opt = Optimizer((A, y))
        opt.train()

        self.assertAlmostEqual(opt.rmse_train, 0.03839898063511659)
        self.assertAlmostEqual(opt.rmse_test, 0.1651279837780928)
        self.assertAlmostEqual(opt.AIC, -97.3500771652472)
        self.assertAlmostEqual(opt.BIC, -88.44635958628555)


if __name__ == '__main__':
    unittest.main()
