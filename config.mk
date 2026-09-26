# dwm-titus version
VERSION = 0.7.2

# Customize below to fit your system

# paths
PREFIX ?= /usr/local
LOCALBASE ?= /usr/local
HOST_OS ?= $(shell uname -s)
MANPREFIX ?= ${PREFIX}/share/man
ifeq (${HOST_OS},FreeBSD)
XSESSIONSDIR ?= ${PREFIX}/share/xsessions
else
XSESSIONSDIR ?= /usr/share/xsessions
endif
PKG_CONFIG ?= pkg-config

# Xinerama, comment if you don't want it
XINERAMALIBS  = -lXinerama
XINERAMAFLAGS = -DXINERAMA

# Portable X11 and library discovery
PKG_MODULES = x11 xft xinerama xrender imlib2 x11-xcb xcb xcb-res fontconfig freetype2
INCS = $(shell ${PKG_CONFIG} --cflags ${PKG_MODULES})
LIBS = $(shell ${PKG_CONFIG} --libs ${PKG_MODULES}) ${KVMLIB}

# Keep release artifacts portable by default. Developers can opt into
# host-specific tuning with `make native`.
OPTIMISATIONS ?= -O2
ifeq (${HOST_OS},FreeBSD)
NATIVE_OPTIMISATIONS ?= -O3 -march=native -mtune=native -flto
else
NATIVE_OPTIMISATIONS ?= -O3 -march=native -mtune=native -flto=auto
endif

# flags
CPPFLAGS += -DVERSION=\"${VERSION}\" ${XINERAMAFLAGS} ${INCS}
ifeq (${HOST_OS},FreeBSD)
# Keep the native BSD interfaces visible; libinotify supplies the event API.
CPPFLAGS += -I${LOCALBASE}/include
LIBS += -L${LOCALBASE}/lib -linotify
else
CPPFLAGS += -D_DEFAULT_SOURCE -D_BSD_SOURCE -D_XOPEN_SOURCE=700L
endif
CFLAGS ?= ${OPTIMISATIONS} -std=c99 -pedantic -Wall -Wno-deprecated-declarations
LDLIBS += ${LIBS}

# Solaris
#CFLAGS = -fast ${INCS} -DVERSION=\"${VERSION}\"
#LDFLAGS = ${LIBS}

# compiler and linker
CC ?= cc
