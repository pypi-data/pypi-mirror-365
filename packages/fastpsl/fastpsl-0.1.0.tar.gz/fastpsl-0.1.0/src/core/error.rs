use std::io;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum PslError {
    #[error("HTTP request failed: {0}")]
    Http(#[from] reqwest::Error),
    #[error("IO operation failed: {0}")]
    Io(#[from] io::Error),
    #[error("PSL parsing failed: {0}")]
    Parse(publicsuffix::Error),
}
