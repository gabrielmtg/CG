cmake_minimum_required(VERSION 3.16)
project(hello_triangle LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(OpenGL REQUIRED)
find_package(glfw3 3.3 REQUIRED)

add_executable(${PROJECT_NAME}
    src/main.cpp
    src/glad.c
)

target_include_directories(${PROJECT_NAME} PRIVATE include)

target_link_libraries(${PROJECT_NAME} PRIVATE
    OpenGL::GL
    glfw
    ${CMAKE_DL_LIBS}
)
