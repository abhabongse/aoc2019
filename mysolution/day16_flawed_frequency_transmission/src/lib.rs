use rayon::prelude::*;
use std::cmp::min;
use std::ops::Range;

#[derive(Debug)]
pub struct Signal {
    pub digits: Vec<i32>,
    prefix_sum: Vec<i32>,
}

impl Signal {
    pub fn new(digits: Vec<i32>) -> Self {
        let prefix_sum: Vec<i32> = std::iter::once(&0)
            .chain(digits.iter())
            .scan(0, |state, &x| {
                *state = *state + x;
                Some(*state)
            })
            .collect();
        Signal { digits, prefix_sum }
    }

    fn range_sum(&self, range: Range<usize>) -> i32 {
        if range.start > range.end {
            panic!("invalid range: {:?}", range)
        }
        self.prefix_sum[range.start] - self.prefix_sum[range.end]
    }

    pub fn compute_digit(&self, repeat_size: usize) -> i32 {
        let offsets_and_signs = (repeat_size - 1..self.digits.len())
            .step_by(2 * repeat_size)
            .zip([1, -1].iter().cloned().cycle());
        let accm = offsets_and_signs.fold(0, |accm, (offset, sign)| {
            let lo = min(offset, self.digits.len());
            let hi = min(offset + repeat_size, self.digits.len());
            accm + (sign) * self.range_sum(lo..hi)
        });
        accm.abs() % 10
    }

    pub fn fft_derive(&self) -> Self {
        Self::new(
            (1..=self.digits.len())
                .into_par_iter()
                .map(|x| self.compute_digit(x))
                .collect(),
        )
    }
}
