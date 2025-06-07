import time
import unittest
from ridewithgps.ratelimiter import RateLimiter


class TestRateLimiter(unittest.TestCase):
    def test_acquire_blocks_when_exhausted(self):
        rl = RateLimiter(2, 1)  # 2 tokens per 1 second
        rl.acquire()
        rl.acquire()
        start = time.time()
        rl.acquire()  # Should block until a token is available
        elapsed = time.time() - start
        self.assertGreaterEqual(elapsed, 0.4)  # Should wait at least some time

    def test_repr(self):
        rl = RateLimiter(1, 1)
        r = repr(rl)
        self.assertIn("RateLimiter", r)


if __name__ == "__main__":
    unittest.main()
