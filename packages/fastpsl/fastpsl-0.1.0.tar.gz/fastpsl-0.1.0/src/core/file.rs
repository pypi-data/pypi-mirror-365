use crate::core::error::PslError;
use dirs::cache_dir;
use publicsuffix::List;
use reqwest;
use std::fs;
use std::sync::OnceLock;

static PSL_URL: &str = "https://publicsuffix.org/list/public_suffix_list.dat";

pub(crate) fn load_psl_dat() -> Result<List, PslError> {
    let mut cache_path = cache_dir().expect("Failed to create or locate the cache directory");
    cache_path.push("public_suffix_list.dat");

    if !cache_path.exists() {
        if let Some(parent) = cache_path.parent() {
            fs::create_dir_all(parent)?;
        }
        let content = reqwest::blocking::get(PSL_URL)?.text()?;
        fs::write(&cache_path, &content)?;
        return content.parse().map_err(PslError::Parse);
    }

    let cached = fs::read_to_string(&cache_path)?;
    cached.parse().map_err(PslError::Parse)
}

pub(crate) fn get_psl() -> Result<&'static List, PslError> {
    static PSL: OnceLock<List> = OnceLock::new();
    Ok(PSL.get_or_init(|| load_psl_dat().unwrap()))
}
