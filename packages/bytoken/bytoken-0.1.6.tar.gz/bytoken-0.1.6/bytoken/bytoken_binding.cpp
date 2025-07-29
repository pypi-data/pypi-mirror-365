#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "bytoken.h"

namespace py = pybind11;

PYBIND11_MODULE(_bytoken_core, m) {
    m.doc() = "Core C++ module for bytoken";

    py::class_<ByToken>(m, "_ByTokenBase")
        .def(py::init<>())
        .def("train", &ByToken::train, py::arg("text_corpus"), py::arg("vocab_size"), py::arg("verbose") = false)
        .def("encode", &ByToken::encode, py::arg("text"))
        .def("decode", &ByToken::decode, py::arg("idx"))
        .def("get_stoi", &ByToken::get_stoi)
        .def("get_merges", &ByToken::get_merges)
        .def("set_stoi", &ByToken::set_stoi)
        .def("set_merges", &ByToken::set_merges)
        .def("rebuild_internal_state", &ByToken::rebuild_internal_state);
}