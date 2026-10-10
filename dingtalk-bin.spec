%global __brp_check_rpaths %{nil}
%global debug_package %{nil}
%define _build_id_links none
%undefine __arch_install_post
AutoReqProv: no

# Version can be overridden from the command line, e.g.
#   rpmbuild -ba --define "dt_version 8.2.8.260818002" dingtalk-bin.spec
# Default keeps the last known-good version for a plain `rpmbuild` run.
%{!?dt_version: %global dt_version 8.2.8.260818002}

Name:           dingtalk-bin
Version:        %{dt_version}
Release:        1%{?dist}
Summary:        钉钉

License:        Custom
URL:            https://gov.dingtalk.com
Source0:        https://dtapp-pub.dingtalk.com/dingtalk-desktop/xc_dingtalk_update/linux_deb/Release/com.alibabainc.dingtalk_%{version}_amd64.deb
Source1:        https://tms.dingtalk.com/markets/dingtalk/service-terms-zh
Source2:        dingtalk-bin.desktop
Source3:        dingtalk.svg
Source4:        dingtalk-launcher.sh
Source6:        xdg-open
Source7:        dingtalk-gray-hook.cpp
Source8:        dingtalk-log-hook.cpp
Source9:        ssl_peer_certificate_shim.c
Source10:       ssl_peer_certificate_shim.map
BuildRequires:  dpkg
BuildRequires:  execstack
BuildRequires:  gcc-c++
Requires:       libGLU.so.1
Requires:       libxcrypt-compat
# Use the system cairo instead of the bundled patch library.
Requires:       cairo

%description
钉钉

%prep
%setup -T -c %{name}-%{version}
dpkg -X %{S:0} .
%define BUILD_DIR %{_builddir}/%{name}-%{version}

%build
cp %{S:1} ./LICENSE
g++ -shared -fPIC -O2 -D_GNU_SOURCE -Wl,-z,defs %{S:7} %{S:8} -o dingtalk-gray-hook.so -ldl
gcc -shared -fPIC -O2 -D_GNU_SOURCE -Wl,--version-script=%{S:10} -Wl,-z,defs %{S:9} -o libdingtalk_ssl_peer_certificate_shim.so -ldl

%install
# Main program
install -d %{buildroot}/opt/dingtalk-bin
mv %{BUILD_DIR}/opt/apps/com.alibabainc.dingtalk/files/* %{buildroot}/opt/dingtalk-bin/

# Desktop file
install -Dm644 %{S:2} -t %{buildroot}%{_datarootdir}/applications/

# Icons
install -Dm644 %{S:3} -t %{buildroot}%{_datarootdir}/icons/hicolor/scalable/apps/

# Launcher
install -d %{buildroot}%{_bindir}
install -Dm755 %{S:4} %{buildroot}%{_bindir}/dingtalk

# Patch
# Link the system cairo (this deb does not ship libcairo.so.2).
# Drop bundled copies that clash with Fedora libraries. The set matches
# Flathub com.dingtalk.DingTalk @ c675939 (8.2.8.260818002).
rm -rf %{buildroot}/opt/dingtalk-bin/*Release*/{libm.so.6,libstdc*,libharfbuzz*,libgbm*,libcurl.so.4,libz*,libGL*}
rm -rf %{buildroot}/opt/dingtalk-bin/*Release*/Resources/{i18n/tool/*.exe,qss/mac,web_content/NativeWebContent_*.zip}
# fix chinese input in workbench
rm -rf %{buildroot}/opt/dingtalk-bin/*Release*/libgtk-x11-2.0.so.*
# fix open url
install -Dm755 %{S:6} -t %{buildroot}/opt/dingtalk-bin/*Release*
# keep plain-text newlines on paste (see dingtalk-gray-hook.cpp)
install -Dm755 dingtalk-gray-hook.so -t %{buildroot}/opt/dingtalk-bin/*Release*
install -Dm755 libdingtalk_ssl_peer_certificate_shim.so -t %{buildroot}/opt/dingtalk-bin/*Release*

# fix "cannot enable executable stack" on newer kernels/glibc loader:
# clear the executable-stack (RWE GNU_STACK) flag on all bundled shared objects.
for f in $(find %{buildroot}/opt/dingtalk-bin/*Release* -type f \( -name '*.so' -o -name '*.so.*' \)); do
    if head -c4 "$f" | grep -q ELF; then execstack -c "$f" 2>/dev/null || :; fi
done

%files
%license LICENSE
%{_bindir}/dingtalk
%{_datarootdir}/applications/*
%{_datarootdir}/icons/hicolor/scalable/apps/*
/opt/dingtalk-bin/

%changelog
* Sat Oct 10 2026 local build - 8.2.8.260818002-1
- update to 8.2.8.260818002
- drop bundled harfbuzz, gbm, and GL libraries
- preload an OpenSSL SSL_get_peer_certificate shim for libutforpc

* Sat Oct 10 2026 local build - 8.1.0.6021101-1
- silence idle MojoThreadServiceDelegate::PostDealyedTask stderr spam

* Fri Aug 14 2026 local build - 8.1.0.6021101-1
- preserve newlines when pasting plain text (disable markdown paste gray switch)

* Fri Jul 10 2026 local build - 8.1.0.6021101-1
- parameterize version via --define "dt_version ..."
- use system cairo (drop bundled libcairo.so.2 patch)
- clear executable stack flag on bundled .so (fix load failure on newer kernel)

* Tue Jan 17 2023 zhullyb <zhullyb@outlook.com> - 1.6.0.230113-2
- fix open url

* Tue Jan 17 2023 zhullyb <zhullyb@outlook.com> - 1.6.0.230113-1
- new version
- remove unused lib
- depend libGLU.so.1 and libxcrypt-compat
- use x11 if dingtalk do not support wayland

* Mon May 23 2022 zhullyb <zhullyb@outlook.com> - 1.4.0.20425-2
- Build for Fedora36
