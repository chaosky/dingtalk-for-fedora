#!/bin/sh

# System packages live in /opt. A user-directory install sets DINGTALK_PREFIX
# (see ~/.local/libexec/dingtalk).
root="${DINGTALK_PREFIX:-/opt/dingtalk-bin}"
cd "$root"/*Release*/ || exit 1
export PATH="$(pwd):$PATH"

# 8.2.8 ships only the xcb Qt platform plugin. Honor an explicit override.
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
export QT_PLUGIN_PATH="$(pwd)${QT_PLUGIN_PATH:+:$QT_PLUGIN_PATH}"

if [ -n "${XMODIFIERS:-}" ]; then
    case "$XMODIFIERS" in
        *fcitx*)
            [ -z "${QT_IM_MODULE:-}" ] && export QT_IM_MODULE=fcitx
            [ -z "${GTK_IM_MODULE:-}" ] && export GTK_IM_MODULE=fcitx
            ;;
        *ibus*)
            [ -z "${QT_IM_MODULE:-}" ] && export QT_IM_MODULE=ibus
            [ -z "${GTK_IM_MODULE:-}" ] && export GTK_IM_MODULE=ibus
            ;;
    esac
fi

dtwebview="$(pwd)/plugins/dtwebview"
if [ -d "$dtwebview" ]; then
    export LD_LIBRARY_PATH="$dtwebview${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi

preload=""
if [ -f "$(pwd)/dingtalk-gray-hook.so" ]; then
    preload="$(pwd)/dingtalk-gray-hook.so"
fi
if [ -f "$(pwd)/libdingtalk_ssl_peer_certificate_shim.so" ]; then
    preload="${preload:+$preload:}$(pwd)/libdingtalk_ssl_peer_certificate_shim.so"
fi
if [ -n "$preload" ]; then
    export LD_PRELOAD="$preload${LD_PRELOAD:+:$LD_PRELOAD}"
fi

exec ./com.alibabainc.dingtalk "$@"
