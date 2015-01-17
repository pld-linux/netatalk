 TODO: AFS support?
#
# Conditional build:
%bcond_without	kerberos5	# Kerberos V UAM
%bcond_without	systemtap	# SystemTap/DTrace support
%bcond_without	tracker		# Spotlight support via tracker
#
Summary:	AppleTalk networking programs
Summary(pl.UTF-8):	Klient i serwer AppleTalk
Summary(pt_BR.UTF-8):	Programas para rede AppleTalk
Summary(zh_CN.UTF-8):	Appletalk 和 Appleshare/IP 服务工具
Name:		netatalk
Version:	3.1.7
Release:	1
Epoch:		2
License:	GPL v2+ (with BSD parts)
Group:		Daemons
Source0:	http://downloads.sourceforge.net/netatalk/%{name}-%{version}.tar.bz2
# Source0-md5:	831ec8bf9e084b64f965d16c528af299
Source1:	%{name}.init
Source2:	%{name}.pamd
Source3:	%{name}.sysconfig
Source4:	ICDumpSuffixMap
URL:		http://www.umich.edu/~rsug/netatalk/
BuildRequires:	acl-devel
BuildRequires:	attr-devel
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake
BuildRequires:	avahi-devel
BuildRequires:	bison
BuildRequires:	cracklib-devel
BuildRequires:	db-devel >= 4.6.0
BuildRequires:	dbus-devel >= 1.1
BuildRequires:	dbus-glib-devel
BuildRequires:	docbook-dtd412-xml
BuildRequires:	docbook-style-xsl
BuildRequires:	flex
BuildRequires:	gettext-tools
BuildRequires:	glib2-devel >= 2.0
%{?with_kerberos5:BuildRequires:	heimdal-devel}
BuildRequires:	libevent-devel
BuildRequires:	libgcrypt >= 1.4.5
BuildRequires:	libltdl-devel
BuildRequires:	libtool
BuildRequires:	libwrap-devel
BuildRequires:	libxslt-progs
BuildRequires:	mysql-devel
BuildRequires:	openldap-devel
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	pam-devel
BuildRequires:	perl-base
BuildRequires:	pkgconfig
BuildRequires:	sed >= 4.0
%{?with_systemtap:BuildRequires:	systemtap-sdt-devel}
BuildRequires:	tdb-devel
%{?with_tracker:BuildRequires:	tracker-devel >= 1.0}
Requires(post):	/sbin/ldconfig
Requires(post,preun):	/sbin/chkconfig
Requires:	dbus >= 1.1
Requires:	libgcrypt >= 1.4.5
Requires:	pam >= 0.99.7.1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# it uses ${_localstatedir}/netatalk
%define		_localstatedir	/var/lib

%description
This package enables Linux to talk to Macintosh computers via the
AppleTalk networking protocol. It includes a daemon to allow Linux to
act as a file server over EtherTalk or IP for Mac's.

%description -l pl.UTF-8
Pakiet ten pozwala na komunikację Linuksa z komputerami Macintosh za
pośrednictwem protokołu AppleTalk. Zawiera demona umożliwiającego, aby
Linux służył jako serwer plików poprzez EtherTalk lub IP dla klientów
Mac.

%description -l pt_BR.UTF-8
Este pacote habilita o Linux a servir computadores Macintosh através
do protocolo AppleTalk.

%package devel
Summary:	Headers and static libraries for Appletalk development
Summary(pl.UTF-8):	Pliki nagłówkowe i biblioteki statyczne Appletalk
Summary(pt_BR.UTF-8):	Arquivos de inclusão e bibliotecas para o desenvolvimento de aplicativos baseados no protocolo AppleTalk
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description devel
This packge contains the header files, and static libraries for
building Appletalk networking programs.

%description devel -l pl.UTF-8
Pakiet ten zawiera pliki nagłówkowe i biblioteki statyczne serwera
AppleTalk.

%description devel -l pt_BR.UTF-8
Arquivos de inclusão e bibliotecas para o desenvolvimento de
aplicativos baseados no protocolo AppleTalk.

%prep
%setup -q

%{__sed} -i -e '1s,/usr/bin/env python,/usr/bin/python,' contrib/shell_utils/afpstats

%build
%{__libtoolize}
%{__aclocal} -I macros
%{__autoconf}
%{__automake}
%{__autoheader}
# "ac_cv_header_dns_sd_h=no" passes over mDNSResponder check to native avahi check
# "netatalk_cv_iconv=no" is a hack to use iconv from glibc even if libiconv exists
# "--with-init-style=debian-systemd" installs systemd service file in PLD-compatible location
# "--without-tdb" disables bundled tdb in favour of system
%configure \
	ac_cv_header_dns_sd_h=no \
	netatalk_cv_iconv=no \
	--disable-silent-rules \
	%{?with_kerberos5:--enable-krbV-uam} \
	--enable-lastdid \
	--enable-pgp-uam \
	--enable-timelord \
	--with-config-dir=%{_sysconfdir}/atalk \
	--with-msg-dir=%{_sysconfdir}/atalk/msg \
	--with-pkgconfdir=%{_sysconfdir}/atalk \
	--with-uams-path=%{_libdir}/atalk \
	--with-cracklib=%{_datadir}/dict/cracklib_dict \
	%{!?with_systemtap:--without-dtrace} \
	--with-init-style=debian-systemd \
	--with-libevent=%{_libdir} \
	--with-pam \
	--with-shadow \
	--with-ssl \
	--with-tcp-wrappers \
	--without-tdb \
	--with-tracker-pkgconfig-version=%{?with_tracker:1.0}%{!?with_tracker:no}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,pam.d,security,sysconfig,atalk/msg}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	MANDIR=$RPM_BUILD_ROOT%{_mandir} \
	m4datadir=%{_aclocaldir}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/atalk
install %{SOURCE2} $RPM_BUILD_ROOT/etc/pam.d/netatalk
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/netatalk
install %{SOURCE4} .

> $RPM_BUILD_ROOT/etc/security/blacklist.netatalk

# loadable modules
%{__rm} $RPM_BUILD_ROOT%{_libdir}/atalk/*.{la,a}
# obsolete(?) utility
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man1/uniconv.1

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
/sbin/chkconfig --add atalk
if [ "$1" = "1" ] ; then
	echo "Run \"/etc/rc.d/init.d/atalk start\" to start netatalk." >&2
fi

%preun
if [ "$1" = "0" ]; then
	/etc/rc.d/init.d/atalk stop >&2
	/sbin/chkconfig --del atalk
fi

%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS CONTRIBUTORS COPYRIGHT NEWS ICDumpSuffixMap doc/manual/*.html
%dir %{_sysconfdir}/atalk
%dir %{_sysconfdir}/atalk/msg
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/atalk/afp.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/atalk/extmap.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/atalk/dbus-session.conf

%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/dbus-1/system.d/netatalk-dbus.conf

%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/netatalk
%attr(754,root,root) %config /etc/rc.d/init.d/atalk
%{systemdunitdir}/netatalk.service

%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/pam.d/netatalk
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/security/blacklist.netatalk

%attr(755,root,root) %{_bindir}/ad
%attr(755,root,root) %{_bindir}/afpldaptest
%attr(755,root,root) %{_bindir}/afppasswd
%attr(755,root,root) %{_bindir}/afpstats
%attr(755,root,root) %{_bindir}/apple_dump
%attr(755,root,root) %{_bindir}/asip-status.pl
%attr(755,root,root) %{_bindir}/cnid2_create
%attr(755,root,root) %{_bindir}/dbd
%attr(755,root,root) %{_bindir}/macusers
%attr(755,root,root) %{_sbindir}/afpd
%attr(755,root,root) %{_sbindir}/cnid_dbd
%attr(755,root,root) %{_sbindir}/cnid_metad
%attr(755,root,root) %{_sbindir}/netatalk
%attr(755,root,root) %{_libdir}/libatalk.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libatalk.so.16
%dir %{_libdir}/atalk
%attr(755,root,root) %{_libdir}/atalk/uams_*.so
%{_mandir}/man1/ad.1*
%{_mandir}/man1/afpldaptest.1*
%{_mandir}/man1/afppasswd.1*
%{_mandir}/man1/afpstats.1*
%{_mandir}/man1/apple_dump.1*
%{_mandir}/man1/asip-status.pl.1*
%{_mandir}/man1/dbd.1*
%{_mandir}/man1/macusers.1*
%{_mandir}/man5/afp.conf.5*
%{_mandir}/man5/afp_signature.conf.5*
%{_mandir}/man5/afp_voluuid.conf.5*
%{_mandir}/man5/extmap.conf.5*
%{_mandir}/man8/afpd.8*
%{_mandir}/man8/cnid_dbd.8*
%{_mandir}/man8/cnid_metad.8*
%{_mandir}/man8/netatalk.8*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/netatalk-config
%attr(755,root,root) %{_libdir}/libatalk.so
%{_libdir}/libatalk.a
%{_libdir}/libatalk.la
%{_includedir}/atalk
%{_aclocaldir}/netatalk.m4
%{_mandir}/man1/netatalk-config.1*
