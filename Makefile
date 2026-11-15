GBDK_HOME ?= ../gbdk
LCC = $(GBDK_HOME)/bin/lcc
ROM = Halcones-Estelares-GB.gb
all: $(ROM)
$(ROM): src/main.c src/assets.h src/hud.h src/moai.h src/audio.h src/waves.h src/player.h src/packed.h src/sprites.h src/boss.h
	$(LCC) -msm83:gb -Wl-yt0 -Wl-yo2 -Wm-ynHALCONESGB -Wl-m -Wl-j -o $(ROM) src/main.c
assets:
	python3 tools/assets.py
clean:
	rm -f $(ROM) src/*.asm src/*.lst src/*.rel src/*.sym src/*.noi src/*.map
.PHONY: all assets clean
