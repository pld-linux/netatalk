# TODO: AFS support?
# system talloc
#
# Conditional build:
%bcond_without	kerberos5	# Kerberos V UAM
%bcond_without	systemtap	# SystemTap/DTrace support
%bcond_without	tracker		# Spotlight support via tracker
#
Summary:	Netatalk AFP fileserver for Apple clients
Summary(pl.UTF-8):	Netatalk - serwer plików AFP dla klientów Apple
Name:		netatalk
Version:	3.1.7
Release:	2
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
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}
Requires:	dbus >= 1.1
Requires:	libgcrypt >= 1.4.5
Requires:	pam >= 0.99.7.1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# it uses ${_localstatedir}/netatalk
%define		_localstatedir	/var/lib

%description
Netatalk is a freely-available Open Source AFP fileserver. A *NIX/*BSD
system running Netatalk is capable of serving many Apple clients
simultaneously as an AppleShare file server (AFP).

%description -l pl.UTF-8
Netatalk to wolnodostępny, mający otwarte źródła serwer plików oparty
na protokole AFP. System uniksowy z działającym Netatalkiem potrafi
serwować wielu klientom Apple jednocześnie jako serwer plików
AppleShare (AFP).

%package libs
Summary:	Netatalk shared library
Summary(pl.UTF-8):	Biblioteka współdzielona Netatalk
Group:		Libraries
Conflicts:	netatalk < 2:3.1.7-2

%description libs
Netatalk shared library.

%description libs -l pl.UTF-8
Biblioteka współdzielona Netatalk.

%package devel
Summary:	Header files for Netatalk development
Summary(pl.UTF-8):	Pliki nagłówkowe Netatalk
Summary(pt_BR.UTF-8):	Arquivos de inclusão para o desenvolvimento de aplicativos baseados no protocolo Netatalk
Group:		Development/Libraries
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}
Requires:	acl-devel
Requires:	attr-devel
Requires:	cracklib-devel
Requires:	libwrap-devel
Requires:	mysql-devel
Requires:	openldap-devel
Requires:	openssl-devel
Requires:	pam-devel
Requires:	tdb-devel

%description devel
This packge contains the header files for building Netatalk
networking programs.

%description devel -l pl.UTF-8
Ten pakiet zawiera pliki nagłówkowe do tworzenia oprogramowania
wykorzystującego protokół Netatalk.

%description devel -l pt_BR.UTF-8
Arquivos de inclusão para o desenvolvimento de aplicativos baseados no
protocolo Netatalk.

%package static
Summary:	Static Netatalk library
Summary(pl.UTF-8):	Statyczna biblioteka Netatalk
Group:		Development/Libraries
Requires:	%{name}-devel = %{epoch}:%{version}-%{release}

%description static
Static Netatalk library.

%description static -l pl.UTF-8
Statyczna biblioteka Netatalk.

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
	--with-docbook=%{_datadir}/sgml/docbook/xsl-stylesheets \
	%{!?with_systemtap:--without-dtrace} \
	--with-init-style=debian-systemd \
	--with-libevent-lib=%{_libdir} \
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
/sbin/chkconfig --add atalk
if [ "$1" = "1" ] ; then
	echo "Run \"/etc/rc.d/init.d/atalk start\" to start netatalk." >&2
fi

%preun
if [ "$1" = "0" ]; then
	/etc/rc.d/init.d/atalk stop >&2
	/sbin/chkconfig --del atalk
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

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

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libatalk.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libatalk.so.16

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/netatalk-config
%attr(755,root,root) %{_libdir}/libatalk.so
%{_libdir}/libatalk.la
%{_includedir}/atalk
%{_aclocaldir}/netatalk.m4
%{_mandir}/man1/netatalk-config.1*

%files static
%defattr(644,root,root,755)
%{_libdir}/libatalk.a
