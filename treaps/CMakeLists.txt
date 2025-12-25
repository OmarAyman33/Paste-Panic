cmake_minimum_required(VERSION 3.10)
project(treaps)

set(CMAKE_CXX_STANDARD 14)
set(PYBIND11_FINDPYTHON ON) 

find_package(pybind11 REQUIRED)

pybind11_add_module(implicit_treap Header.h)
pybind11_add_module(leaderboard_treap leaderboard_treap.h)