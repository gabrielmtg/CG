CXX      := g++
CC       := gcc

CPPFLAGS := -Iinclude -MMD -MP
CXXFLAGS := -std=c++17 -Wall -Wextra -O2
CFLAGS   := -Wall -Wextra -O2
LDLIBS   := -lglfw -lGL -ldl -lpthread

BUILD_DIR := build
TARGET    := $(BUILD_DIR)/robot

SRCS_CXX := $(wildcard src/*.cpp)
SRCS_C   := $(wildcard src/*.c)

OBJS := $(SRCS_CXX:src/%.cpp=$(BUILD_DIR)/%.o) \
        $(SRCS_C:src/%.c=$(BUILD_DIR)/%.o)
DEPS := $(OBJS:.o=.d)

.PHONY: all run clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $^ -o $@ $(LDLIBS)

$(BUILD_DIR)/%.o: src/%.cpp
	@mkdir -p $(dir $@)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

$(BUILD_DIR)/%.o: src/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

# o vscode do snap muda umas variaveis de ambiente e o glfw trava ao abrir a janela
# entao aqui volta o ambiente original antes de rodar
ifdef XDG_DATA_DIRS_VSCODE_SNAP_ORIG
RUN_ENV := env -u GSETTINGS_SCHEMA_DIR XDG_DATA_DIRS="$(XDG_DATA_DIRS_VSCODE_SNAP_ORIG)"
endif

run: all
	$(RUN_ENV) ./$(TARGET)

clean:
	rm -rf $(BUILD_DIR)

-include $(DEPS)
