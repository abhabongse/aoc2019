use std::env;
use std::fs;
use std::time::Instant;

use day16_flawed_frequency_transmission::Signal;

fn main() {
    let contents = fs::read_to_string(env::args().nth(1).unwrap()).unwrap();
    let digits: Vec<i32> = contents.chars()
        .filter_map(|x| x.to_digit(10))
        .map(|x| x as i32)
        .collect();
    part1_solve(digits.as_ref());
    part2_solve(digits.as_ref());
}

fn part1_solve(digits: &[i32]) {
    let mut signal = Signal::new(digits.into());
    for _ in 0..100 { signal = signal.fft_derive(); }
    let output = &signal.digits[..8];
    println!("{:?}", output);
}

fn part2_solve(digits: &[i32]) {
    let offset = digits.iter().take(7).fold(0, |acc, x| acc * 10 + (*x)) as usize;
    let ext_digits: Vec<i32> = std::iter::repeat(digits.iter())
        .take(10_000)
        .flatten()
        .cloned()
        .collect();
    let mut signal = Signal::new(ext_digits);
    let now = Instant::now();
    for r in 1..=100 {
        signal = signal.fft_derive();
        println!("round {} done in {:.2} seconds", r, now.elapsed().as_secs_f64());
    }
    let output = &signal.digits[offset..offset + 8];
    println!("{:?}", output);
}
