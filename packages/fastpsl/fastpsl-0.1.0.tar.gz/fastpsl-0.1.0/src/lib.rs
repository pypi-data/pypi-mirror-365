mod core;
use crate::core::parse::parse_domain;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyString};

#[pyclass(get_all)]
#[derive(Clone)]
struct ExtractResult {
    /// subdomain (e.g. api.example.com → api)
    subdomain: String,
    /// root domain (e.g. example.com → example)
    domain: String,
    /// TLD (e.g. example.com -> com)
    suffix: String,
    /// is private domain type
    is_private: bool,
}

#[pymethods]
impl ExtractResult {
    fn __str__(&self) -> PyResult<String> {
        Ok(format!(
            "ExtractResult(subdomain='{}', domain='{}', suffix='{}', is_private={})",
            self.subdomain, self.domain, self.suffix, self.is_private,
        ))
    }
    fn __repr__(&self) -> PyResult<String> {
        self.__str__()
    }
}

#[pyfunction]
fn extract(domain: Bound<'_, PyAny>) -> PyResult<ExtractResult> {
    let domain_str = if let Ok(py_str) = domain.downcast::<PyString>() {
        py_str.to_string()
    } else if let Ok(py_bytes) = domain.downcast::<PyBytes>() {
        py_bytes.to_string()
    } else {
        return Err(pyo3::exceptions::PyTypeError::new_err(
            "Domain type must be either `str` or `bytes`.",
        ));
    };

    let domain_info = parse_domain(domain_str).unwrap();

    Ok(ExtractResult {
        subdomain: domain_info.subdomain,
        domain: domain_info.domain,
        suffix: domain_info.suffix,
        is_private: domain_info.is_private,
    })
}

#[pymodule]
fn fastpsl(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract, m)?)?;
    m.add_class::<ExtractResult>()?;
    Ok(())
}
