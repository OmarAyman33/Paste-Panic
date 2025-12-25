cmake_minimum_required(VERSION 3.10)
project(treaps)

set(CMAKE_CXX_STANDARD 14)
set(PYBIND11_FINDPYTHON ON) 

find_package(pybind11 REQUIRED)

pybind11_add_module(implicit_treap implicit_treap/implicit-Treap/Treap/implicitTreap.cpp) 
pybind11_add_module(leaderboard_treap leaderboard_treap/leaderboard_treap.cpp)

# let the linker know that the header files are written in C++ 
set_target_properties(implicit_treap PROPERTIES LINKER_LANGUAGE CXX)
set_target_properties(leaderboard_treap PROPERTIES LINKER_LANGUAGE CXX)