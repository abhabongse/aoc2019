use std::env;
use std::fs;

use indicatif::{ProgressBar, ProgressStyle};

use day16_flawed_frequency_transmission::Signal;

fn main() {
    let in_file = env::args().nth(1).expect("expected input file");
    let contents = fs::read_to_string(in_file).expect("file exists");
    let digits: Vec<i32> = contents
        .chars()
        .filter_map(|x| x.to_digit(10))
        .map(|x| x as i32)
        .collect();
    part1_solve(digits.as_ref());
    part2_solve(digits.as_ref());
}

fn part1_solve(digits: &[i32]) {
    let mut signal = Signal::new(digits.into());
    for _ in 0..100 {
        signal = signal.fft_derive();
    }
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

    let pb = ProgressBar::new(100);
    pb.set_style(
        ProgressStyle::default_bar()
            .template("{elapsed_precise}/-{eta_precise} {wide_bar} {pos:>3}/{len:3}"),
    );

    // let now = Instant::now();
    for r in 1..=100 {
        signal = signal.fft_derive();
        pb.set_message(format!("round #{}", r).as_str());
        pb.inc(1);
    }
    pb.finish();
    let output = &signal.digits[offset..offset + 8];
    println!("{:?}", output);
}
