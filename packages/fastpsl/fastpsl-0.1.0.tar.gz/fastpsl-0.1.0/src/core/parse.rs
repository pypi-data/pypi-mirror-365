use std::sync::OnceLock;

use crate::core::error::PslError;
use crate::core::file::get_psl;
use publicsuffix::{Psl, Type};
use regex::Regex;

#[derive(Clone)]
pub struct DomainInfo {
    /// subdomain (e.g. api.example.com → api)
    pub subdomain: String,
    /// root domain (e.g. example.com → example)
    pub domain: String,
    /// TLD (e.g. example.com -> com)
    pub suffix: String,
    /// is private domain type
    pub is_private: bool,
}

pub fn extract_parts(full: &str, suffix: &str) -> (String, String) {
    // Remove the suffix (including the preceding `.`)
    let suffix_with_dot = format!(".{}", suffix);
    if !full.ends_with(&suffix_with_dot) {
        return ("".into(), "".into()); // Invalid input case
    }

    // Cut off the suffix and the last dot
    let without_suffix = &full[..full.len() - suffix_with_dot.len()];

    // Find the last dot; the part before is the subdomain, and the part after is the root domain
    if let Some(pos) = without_suffix.rfind('.') {
        let subdomain = &without_suffix[..pos];
        let root = &without_suffix[pos + 1..];
        (subdomain.to_string(), root.to_string())
    } else {
        // No dot, indicating no subdomain
        ("".into(), without_suffix.to_string())
    }
}

/// Strip scheme/user/password/port/path etc. from the original input string, keeping only the hostname
pub fn extract_hostname_from_input(input: &str) -> Option<String> {
    static HOST_RE: OnceLock<Regex> = OnceLock::new();
    let re = HOST_RE.get_or_init(|| {
        Regex::new(r"^(?:[a-zA-Z][a-zA-Z0-9+\-.]*://)?(?:[^@]+@)?([^:/?#]+)").unwrap()
    });

    re.captures(input)
        .and_then(|caps| caps.get(1))
        .map(|m| m.as_str().to_string())
}

pub fn parse_domain(input: String) -> Result<DomainInfo, PslError> {
    let input = extract_hostname_from_input(input.as_str()).unwrap();

    let psl = get_psl()?;

    if let Some(domain) = psl.domain(input.as_bytes()) {
        let suffix = std::str::from_utf8(domain.suffix().as_bytes())
            .unwrap()
            .to_string();

        let is_private = domain.suffix().typ() == Some(Type::Private);

        let (subdomain, root) = extract_parts(input.as_str(), &suffix);

        Ok(DomainInfo {
            subdomain: subdomain,
            domain: root,
            suffix: suffix,
            is_private: is_private,
        })
    } else {
        let (suffix, is_private) = if let Some(suffix) = psl.suffix(input.as_bytes()) {
            (
                std::str::from_utf8(suffix.as_bytes()).unwrap().to_string(),
                suffix.typ() == Some(Type::Private),
            )
        } else {
            ("".into(), false)
        };

        Ok(DomainInfo {
            subdomain: "".into(),
            domain: "".into(),
            suffix: suffix,
            is_private: is_private,
        })
    }
}
